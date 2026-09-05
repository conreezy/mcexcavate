from pathlib import Path
from smtplib import SMTPDataError
from tempfile import TemporaryDirectory
from unittest.mock import patch
import uuid

from django.core import mail
from django.test import TestCase, override_settings
from django.utils import timezone
from PIL import Image

from mcexcavate import views
from .lead_queue import PHOTO_COMPRESSION_STEPS, process_next_lead_email
from .models import LeadSubmission, LeadSubmissionImage


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class LeadPhotoFallbackTests(TestCase):
    def setUp(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.media = Path(directory.name)
        media_settings = override_settings(MEDIA_ROOT=directory.name)
        media_settings.enable()
        self.addCleanup(media_settings.disable)
        self.lead = LeadSubmission.objects.create(
            name='Photo Lead', email='customer@example.com', service='Concrete Slabs',
            recipient_emails='estimator@example.com', email_next_attempt_at=timezone.now(),
        )

    def add_photo(self, size=(1800, 1600), format='BMP', noisy=False):
        relative_path = 'form_uploads/{}.{}'.format(uuid.uuid4().hex, format.lower())
        path = self.media / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        photo = Image.effect_noise(size, 100).convert('RGB') if noisy else Image.new('RGB', size, 'blue')
        photo.save(path, format, quality=95)
        return LeadSubmissionImage.objects.create(
            lead=self.lead, file=relative_path, original_name='customer-original.' + format.lower(),
            file_size=path.stat().st_size, content_type='image/' + format.lower(),
        )

    def assert_attachments_match_saved_photos(self):
        self.lead.refresh_from_db()
        self.assertEqual(self.lead.email_status, LeadSubmission.STATUS_SENT)
        self.assertEqual(len(mail.outbox), 1)
        saved_photos = list(self.lead.images.all())
        self.assertEqual(len(mail.outbox[0].attachments), len(saved_photos))
        for attachment, photo in zip(mail.outbox[0].attachments, saved_photos):
            data = Path(photo.absolute_path).read_bytes()
            self.assertEqual(attachment[1], data)
            self.assertEqual(photo.file_size, len(data))
            self.assertEqual(photo.content_type, 'image/jpeg')
            self.assertEqual(attachment[2], 'image/jpeg')
        self.assertLessEqual(sum(photo.file_size for photo in saved_photos), views.LEAD_EMAIL_MAX_ATTACHMENT_BYTES)
        self.assertLessEqual(len(mail.outbox[0].message().as_bytes(linesep='\r\n')), views.LEAD_EMAIL_MAX_MESSAGE_BYTES)

    def test_normal_email_does_not_recompress_or_replace_photos(self):
        photo = self.add_photo(size=(100, 80), format='JPEG')
        path = photo.absolute_path
        data = Path(path).read_bytes()
        with patch('project.lead_queue._recompress_photos') as compress:
            self.assertTrue(process_next_lead_email())
            compress.assert_not_called()
        photo.refresh_from_db()
        self.assertEqual(photo.absolute_path, path)
        self.assertEqual(Path(path).read_bytes(), data)
        self.assert_attachments_match_saved_photos()

    def test_oversized_legacy_photos_are_replaced_then_emailed(self):
        photos = [self.add_photo() for _ in range(2)]
        originals = [Path(photo.absolute_path) for photo in photos]
        self.assertGreater(sum(path.stat().st_size for path in originals), views.LEAD_EMAIL_MAX_ATTACHMENT_BYTES)
        self.assertTrue(process_next_lead_email())
        self.assert_attachments_match_saved_photos()
        for original in originals:
            self.assertFalse(original.exists())
        for photo in self.lead.images.all():
            self.assertEqual(photo.original_name, 'customer-original.bmp')
            with Image.open(photo.absolute_path) as saved:
                self.assertEqual(saved.format, 'JPEG')
                self.assertLessEqual(max(saved.size), 1280)
        self.assertEqual(len(list(self.media.rglob('*.jpg'))), 2)

    def test_encoded_email_limit_also_triggers_fallback(self):
        photo = self.add_photo(size=(1200, 1000), format='JPEG', noisy=True)
        original = Path(photo.absolute_path)
        self.assertLess(photo.file_size, views.LEAD_EMAIL_MAX_ATTACHMENT_BYTES)
        with patch.object(views, 'LEAD_EMAIL_MAX_MESSAGE_BYTES', 150_000):
            process_next_lead_email()
            self.assert_attachments_match_saved_photos()
        self.assertFalse(original.exists())
        with Image.open(self.lead.images.get().absolute_path) as saved:
            self.assertLessEqual(max(saved.size), 640)

    def test_smtp_retry_reuses_reduced_files_without_compressing_again(self):
        for _ in range(2):
            self.add_photo()
        with patch('django.core.mail.EmailMessage.send', side_effect=SMTPDataError(451, b'Try later')):
            process_next_lead_email()
        self.lead.refresh_from_db()
        self.assertEqual(self.lead.email_status, LeadSubmission.STATUS_PENDING)
        files = {photo.file.name: Path(photo.absolute_path).read_bytes() for photo in self.lead.images.all()}
        LeadSubmission.objects.filter(pk=self.lead.pk).update(email_next_attempt_at=timezone.now())
        with patch('project.lead_queue._recompress_photos') as compress:
            process_next_lead_email()
            compress.assert_not_called()
        self.assert_attachments_match_saved_photos()
        self.assertEqual(files, {photo.file.name: Path(photo.absolute_path).read_bytes() for photo in self.lead.images.all()})

    def test_database_failure_keeps_original_file_and_removes_replacement(self):
        photo = self.add_photo()
        original_name, original_size = photo.file.name, photo.file_size
        original_data = Path(photo.absolute_path).read_bytes()
        with patch.object(views, 'LEAD_EMAIL_MAX_ATTACHMENT_BYTES', 100_000), \
                patch.object(LeadSubmissionImage, 'save', side_effect=RuntimeError('Database write failed')):
            process_next_lead_email()
        photo.refresh_from_db()
        self.lead.refresh_from_db()
        self.assertEqual(self.lead.email_status, LeadSubmission.STATUS_FAILED)
        self.assertEqual(photo.file.name, original_name)
        self.assertEqual(photo.file_size, original_size)
        self.assertEqual(Path(photo.absolute_path).read_bytes(), original_data)
        self.assertEqual([path for path in self.media.rglob('*') if path.is_file()], [Path(photo.absolute_path)])
        self.assertEqual(len(mail.outbox), 0)

    def test_recompression_encode_failure_keeps_original(self):
        photo = self.add_photo()
        original_data = Path(photo.absolute_path).read_bytes()
        with patch.object(views, 'LEAD_EMAIL_MAX_ATTACHMENT_BYTES', 100_000), \
                patch('PIL.Image.Image.save', side_effect=OSError('Disk full')):
            process_next_lead_email()
        self.assertEqual(Path(photo.absolute_path).read_bytes(), original_data)
        self.assertEqual(list(self.media.rglob('*.jpg')), [])
        self.assertEqual(len(mail.outbox), 0)

    def test_lost_worker_claim_discards_replacement_and_keeps_original(self):
        from mcexcavate.lead_images import save_contact_photo

        photo = self.add_photo()
        original_data = Path(photo.absolute_path).read_bytes()
        newer_token = uuid.uuid4()

        def replaced_worker(*args, **kwargs):
            path = save_contact_photo(*args, **kwargs)
            LeadSubmission.objects.filter(pk=self.lead.pk).update(email_claim_token=newer_token)
            return path

        with patch.object(views, 'LEAD_EMAIL_MAX_ATTACHMENT_BYTES', 100_000), \
                patch('mcexcavate.lead_images.save_contact_photo', side_effect=replaced_worker):
            process_next_lead_email()
        self.lead.refresh_from_db()
        self.assertEqual(self.lead.email_status, LeadSubmission.STATUS_SENDING)
        self.assertEqual(self.lead.email_claim_token, newer_token)
        self.assertEqual(Path(photo.absolute_path).read_bytes(), original_data)
        self.assertEqual(list(self.media.rglob('*.jpg')), [])
        self.assertEqual(len(mail.outbox), 0)

    def test_unfixable_size_stops_after_bounded_compression_without_sending(self):
        self.add_photo(format='JPEG')
        from .lead_queue import _recompress_photos
        with patch.object(views, 'LEAD_EMAIL_MAX_ATTACHMENT_BYTES', 1), \
                patch('project.lead_queue._recompress_photos', wraps=_recompress_photos) as compress:
            process_next_lead_email()
            self.assertEqual(compress.call_count, len(PHOTO_COMPRESSION_STEPS))
        self.lead.refresh_from_db()
        self.assertEqual(self.lead.email_status, LeadSubmission.STATUS_FAILED)
        self.assertIn('still exceeds', self.lead.email_error)
        self.assertIsNone(self.lead.email_next_attempt_at)
        self.assertEqual(len(mail.outbox), 0)

    def test_oversized_message_text_does_not_needlessly_reduce_photos(self):
        photo = self.add_photo(format='JPEG')
        data = Path(photo.absolute_path).read_bytes()
        self.lead.message = 'X' * 5000
        self.lead.save(update_fields=['message'])
        with patch.object(views, 'LEAD_EMAIL_MAX_MESSAGE_BYTES', 2000), \
                patch('project.lead_queue._recompress_photos') as compress:
            process_next_lead_email()
            compress.assert_not_called()
        self.lead.refresh_from_db()
        self.assertEqual(self.lead.email_status, LeadSubmission.STATUS_FAILED)
        self.assertIn('text exceeds', self.lead.email_error)
        self.assertEqual(Path(photo.absolute_path).read_bytes(), data)
        self.assertEqual(len(mail.outbox), 0)
