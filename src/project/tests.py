from datetime import timedelta
from io import StringIO
from smtplib import SMTPAuthenticationError, SMTPDataError, SMTPRecipientsRefused
from unittest.mock import patch
import uuid

from django.contrib.admin.sites import AdminSite
from django.core import mail
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.utils import timezone

from .admin import LeadSubmissionAdmin
from .lead_queue import (
    CLAIM_TIMEOUT, MAX_ATTEMPTS, claim_next_lead, deliver_claimed_lead,
    process_next_lead_email, queue_lead_emails,
)
from .models import LeadSubmission, LeadSubmissionImage


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class LeadEmailQueueTests(TestCase):
    def make_lead(self, **overrides):
        fields = dict(name='Test Lead', email='customer@example.com', service='Concrete Slabs',
                      recipient_emails='first@example.com, second@example.com',
                      email_next_attempt_at=timezone.now())
        fields.update(overrides)
        return LeadSubmission.objects.create(**fields)

    def test_worker_sends_once_and_uses_recorded_recipients(self):
        lead = self.make_lead()
        self.assertTrue(process_next_lead_email())
        lead.refresh_from_db()
        self.assertEqual(lead.email_status, LeadSubmission.STATUS_SENT)
        self.assertEqual(lead.email_attempts, 1)
        self.assertIsNotNone(lead.emailed_at)
        self.assertIsNone(lead.email_claim_token)
        self.assertEqual(mail.outbox[0].to, ['first@example.com', 'second@example.com'])
        self.assertEqual(mail.outbox[0].reply_to, ['customer@example.com'])
        self.assertFalse(process_next_lead_email())
        self.assertEqual(len(mail.outbox), 1)

    def test_second_worker_cannot_claim_active_job(self):
        lead = self.make_lead()
        first = claim_next_lead()
        self.assertEqual(first.pk, lead.pk)
        self.assertIsNone(claim_next_lead())
        self.assertEqual(queue_lead_emails(LeadSubmission.objects.all()), 0)

    def test_lost_claim_race_does_not_take_other_workers_job(self):
        lead = self.make_lead()
        from django.db.models.query import QuerySet
        original_update = QuerySet.update
        other_token = uuid.uuid4()

        def race_update(queryset, **kwargs):
            if kwargs.get('email_status') == LeadSubmission.STATUS_SENDING:
                original_update(LeadSubmission.objects.filter(pk=lead.pk),
                                email_status=LeadSubmission.STATUS_SENDING,
                                email_claimed_at=timezone.now(), email_claim_token=other_token,
                                email_next_attempt_at=None, email_attempts=1)
            return original_update(queryset, **kwargs)

        with patch.object(QuerySet, 'update', race_update):
            self.assertIsNone(claim_next_lead())
        lead.refresh_from_db()
        self.assertEqual(lead.email_claim_token, other_token)
        self.assertEqual(lead.email_attempts, 1)

    def test_interrupted_job_can_be_reclaimed_and_old_worker_cannot_send(self):
        self.make_lead()
        old = claim_next_lead()
        LeadSubmission.objects.filter(pk=old.pk).update(email_claimed_at=timezone.now() - CLAIM_TIMEOUT - timedelta(seconds=1))
        new = claim_next_lead()
        self.assertNotEqual(old.email_claim_token, new.email_claim_token)
        self.assertEqual(new.email_attempts, 2)
        deliver_claimed_lead(old)
        self.assertEqual(len(mail.outbox), 0)
        deliver_claimed_lead(new)
        self.assertEqual(len(mail.outbox), 1)

    def test_stale_worker_cannot_overwrite_newer_claim(self):
        lead = self.make_lead()
        old = claim_next_lead()
        newer_token = uuid.uuid4()

        def simulate_restart(*args, **kwargs):
            LeadSubmission.objects.filter(pk=lead.pk).update(email_claim_token=newer_token)

        with patch('mcexcavate.views.send_email_with_attachments', side_effect=simulate_restart):
            deliver_claimed_lead(old)
        lead.refresh_from_db()
        self.assertEqual(lead.email_status, LeadSubmission.STATUS_SENDING)
        self.assertEqual(lead.email_claim_token, newer_token)

    def test_interrupted_final_attempt_is_marked_failed(self):
        lead = self.make_lead(email_status=LeadSubmission.STATUS_SENDING,
                              email_claimed_at=timezone.now() - CLAIM_TIMEOUT - timedelta(seconds=1),
                              email_claim_token=uuid.uuid4(), email_attempts=MAX_ATTEMPTS)
        self.assertIsNone(claim_next_lead())
        lead.refresh_from_db()
        self.assertEqual(lead.email_status, LeadSubmission.STATUS_FAILED)
        self.assertIn('interrupted', lead.email_error)

    @patch('mcexcavate.views.send_email_with_attachments', side_effect=SMTPDataError(451, b'Try later'))
    def test_transient_errors_retry_with_delays_then_stop(self, mocked_send):
        lead = self.make_lead()
        for index, delay in enumerate((60, 300, 900, None), start=1):
            now = timezone.now()
            with patch('project.lead_queue.timezone.now', return_value=now):
                self.assertTrue(process_next_lead_email())
            lead.refresh_from_db()
            self.assertEqual(lead.email_attempts, index)
            self.assertIn('Try later', lead.email_error)
            if delay:
                self.assertEqual(lead.email_status, LeadSubmission.STATUS_PENDING)
                self.assertEqual(lead.email_next_attempt_at, now + timedelta(seconds=delay))
                self.assertFalse(process_next_lead_email())
                LeadSubmission.objects.filter(pk=lead.pk).update(email_next_attempt_at=timezone.now())
            else:
                self.assertEqual(lead.email_status, LeadSubmission.STATUS_FAILED)
                self.assertIsNone(lead.email_next_attempt_at)
        self.assertEqual(mocked_send.call_count, 4)

    def test_permanent_failures_remain_saved_without_automatic_retry(self):
        for error in (SMTPAuthenticationError(535, b'Bad credentials'),
                      SMTPDataError(552, b'Too large'),
                      SMTPRecipientsRefused({'first@example.com': (550, b'No mailbox')}),
                      FileNotFoundError('Photo missing'), ValueError('Invalid message')):
            with self.subTest(error=error):
                lead = self.make_lead()
                with patch('mcexcavate.views.send_email_with_attachments', side_effect=error), \
                        patch('project.lead_queue._recompress_photos') as compress:
                    self.assertTrue(process_next_lead_email())
                    compress.assert_not_called()
                lead.refresh_from_db()
                self.assertEqual(lead.email_status, LeadSubmission.STATUS_FAILED)
                self.assertEqual(lead.email_attempts, 1)
                self.assertIsNone(lead.email_next_attempt_at)
                self.assertFalse(process_next_lead_email())

    def test_missing_attachment_cannot_be_silently_omitted(self):
        lead = self.make_lead()
        LeadSubmissionImage.objects.create(lead=lead, file='nonexistent-photo-for-test.jpg')
        process_next_lead_email()
        lead.refresh_from_db()
        self.assertEqual(lead.email_status, LeadSubmission.STATUS_FAILED)
        self.assertEqual(len(mail.outbox), 0)

    def test_zero_send_result_does_not_mark_sent(self):
        lead = self.make_lead()
        with patch('django.core.mail.EmailMessage.send', return_value=0):
            process_next_lead_email()
        lead.refresh_from_db()
        self.assertEqual(lead.email_status, LeadSubmission.STATUS_PENDING)
        self.assertIsNone(lead.emailed_at)
        self.assertIn('did not accept', lead.email_error)

    def test_existing_and_future_leads_do_not_send_until_due_or_explicitly_queued(self):
        historical = [self.make_lead(email_next_attempt_at=None, email_status=status)
                      for status in (LeadSubmission.STATUS_PENDING, LeadSubmission.STATUS_FAILED, LeadSubmission.STATUS_SENT)]
        self.make_lead(email_next_attempt_at=timezone.now() + timedelta(hours=1))
        self.assertFalse(process_next_lead_email())
        self.assertEqual(queue_lead_emails(LeadSubmission.objects.filter(pk__in=[item.pk for item in historical])), 3)
        self.assertEqual(queue_lead_emails(LeadSubmission.objects.all()), 0)
        self.assertTrue(process_next_lead_email())

    def test_admin_resend_queues_without_sending_and_does_not_reset_pending_job(self):
        lead = self.make_lead(email_status=LeadSubmission.STATUS_FAILED, email_next_attempt_at=None,
                              email_attempts=4, email_error='Authentication failed')
        admin = LeadSubmissionAdmin(LeadSubmission, AdminSite())
        with patch.object(admin, 'message_user'):
            admin.resend_lead_emails(None, LeadSubmission.objects.all())
        lead.refresh_from_db()
        self.assertEqual(lead.email_status, LeadSubmission.STATUS_PENDING)
        self.assertEqual(lead.email_attempts, 0)
        self.assertEqual(lead.email_error, '')
        self.assertIsNotNone(lead.email_next_attempt_at)
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(queue_lead_emails(LeadSubmission.objects.all()), 0)

    def test_command_once_returns_when_queue_is_empty(self):
        output = StringIO()
        call_command('send_lead_emails', once=True, stdout=output)
        self.assertIn('No email is due', output.getvalue())
