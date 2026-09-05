from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, override_settings
from PIL import Image

from .forms import validate_contact_images
from .lead_images import save_contact_photo
from .views import handle_uploaded_files, send_email_with_attachments


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class ContactPhotoTests(SimpleTestCase):
    def upload(self, image, format='PNG', **kwargs):
        data = BytesIO()
        image.save(data, format, **kwargs)
        return SimpleUploadedFile('photo.' + format.lower(), data.getvalue(), content_type='image/' + format.lower())

    def test_exif_orientation_is_preserved_and_metadata_removed(self):
        exif = Image.Exif()
        exif[274] = 6
        exif[270] = 'Original private metadata'
        upload = self.upload(Image.new('RGB', (2400, 1200), 'red'), 'JPEG', exif=exif)
        with TemporaryDirectory() as media_root, self.settings(MEDIA_ROOT=media_root):
            path = save_contact_photo(upload)
            with Image.open(path) as saved:
                self.assertEqual(saved.size, (800, 1600))
                self.assertEqual(dict(saved.getexif()), {})

    def test_small_transparent_photo_becomes_white_background_jpeg_without_enlarging(self):
        upload = self.upload(Image.new('RGBA', (80, 40), (0, 0, 0, 0)))
        with TemporaryDirectory() as media_root, self.settings(MEDIA_ROOT=media_root):
            path = save_contact_photo(upload)
            with Image.open(path) as saved:
                self.assertEqual(saved.size, (80, 40))
                self.assertEqual(saved.format, 'JPEG')
                self.assertEqual(saved.mode, 'RGB')
                self.assertEqual(saved.getpixel((0, 0)), (255, 255, 255))

    def test_large_original_is_accepted_and_only_compact_photo_is_stored(self):
        upload = self.upload(Image.new('RGB', (4000, 3000), 'blue'), 'BMP')
        self.assertGreater(upload.size, 25 * 1024 * 1024)
        validate_contact_images([upload])
        with TemporaryDirectory() as media_root, self.settings(MEDIA_ROOT=media_root):
            path = save_contact_photo(upload)
            self.assertLess(Path(path).stat().st_size, 1024 * 1024)
            self.assertEqual([item for item in Path(media_root).rglob('*') if item.is_file()], [Path(path)])

    def test_later_photo_failure_removes_earlier_processed_photos(self):
        good = self.upload(Image.new('RGB', (100, 100)))
        bad = SimpleUploadedFile('broken.jpg', b'not a photo')
        with TemporaryDirectory() as media_root, self.settings(MEDIA_ROOT=media_root):
            with self.assertLogs('mcexcavate.views', level='ERROR'):
                paths, errors = handle_uploaded_files([good, bad])
            self.assertIsNone(paths)
            self.assertIn('broken.jpg', errors[0])
            self.assertEqual(list(Path(media_root).rglob('*.jpg')), [])

    def test_five_detailed_photos_fit_email_without_recompression(self):
        photo = Image.effect_noise((1600, 1600), 100).convert('RGB')
        with TemporaryDirectory() as media_root, self.settings(MEDIA_ROOT=media_root):
            paths = [save_contact_photo(self.upload(photo)) for _ in range(5)]
            saved_bytes = [Path(path).read_bytes() for path in paths]
            send_email_with_attachments({'name': 'Test', 'email': 'lead@example.com'}, paths, 'Contact')
            self.assertLess(len(mail.outbox[0].message().as_bytes()), 20 * 1024 * 1024)
            self.assertEqual([item[1] for item in mail.outbox[0].attachments], saved_bytes)

    def test_oversized_legacy_attachments_fail_without_smtp_send(self):
        with patch('mcexcavate.views.os.path.getsize', return_value=13 * 1024 * 1024), \
                patch('django.core.mail.EmailMessage.send') as send:
            with self.assertRaisesRegex(ValueError, 'attachment budget'):
                send_email_with_attachments({}, ['old-original.jpg'], 'Contact')
            send.assert_not_called()
