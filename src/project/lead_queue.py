"""A durable email outbox on LeadSubmission, compatible with SQLite."""
import logging
import os
import uuid
from datetime import timedelta
from smtplib import (
    SMTPAuthenticationError, SMTPException, SMTPRecipientsRefused,
    SMTPResponseException,
)

from django.conf import settings
from django.db import transaction
from django.db.models import F, Q
from django.utils import timezone

from .models import LeadSubmission


logger = logging.getLogger(__name__)
MAX_ATTEMPTS = 4
RETRY_DELAYS = (60, 300, 900)
CLAIM_TIMEOUT = timedelta(minutes=10)
PHOTO_COMPRESSION_STEPS = ((1280, 70), (960, 60), (640, 50), (320, 40))


class LeadClaimLost(Exception):
    """A newer worker owns this job; this worker must stop."""


def _recompress_photos(lead, owned, max_dimension, quality):
    from mcexcavate.lead_images import remove_uploaded_files, save_contact_photo

    for photo in lead.images.all():
        # Keep the lease alive during fallback and stop if ownership changed.
        if not owned.update(email_claimed_at=timezone.now()):
            raise LeadClaimLost()
        original_path = photo.absolute_path
        with open(original_path, 'rb') as source:
            replacement_path = save_contact_photo(source, max_dimension=max_dimension, quality=quality)
        try:
            size = os.path.getsize(replacement_path)
            if size >= os.path.getsize(original_path):
                remove_uploaded_files([replacement_path])
                continue
            # Switch the database reference only after the whole JPEG is saved.
            # A failed write leaves the original file/reference available.
            with transaction.atomic():
                if not owned.update(email_claimed_at=timezone.now()):
                    raise LeadClaimLost()
                photo.file = os.path.relpath(replacement_path, settings.MEDIA_ROOT).replace(os.sep, '/')
                photo.file_size = size
                photo.content_type = 'image/jpeg'
                photo.save(update_fields=['file', 'file_size', 'content_type'])
        except Exception:
            remove_uploaded_files([replacement_path])
            raise
        remove_uploaded_files([original_path])


def _send_with_size_fallback(lead, owned):
    from mcexcavate.views import LEAD_EMAIL_RECIPIENTS, LeadEmailTooLarge, send_email_with_attachments

    recipients = [email.strip() for email in lead.recipient_emails.split(',') if email.strip()]
    steps = iter(PHOTO_COMPRESSION_STEPS)
    while True:
        if not owned.update(email_claimed_at=timezone.now()):
            raise LeadClaimLost()
        paths = [photo.absolute_path for photo in lead.images.all()]
        try:
            # All size checks run before SMTP, so fallback cannot duplicate a send.
            send_email_with_attachments(
                lead.as_form_data(), paths, lead.source_page or lead.service,
                recipients=recipients or LEAD_EMAIL_RECIPIENTS,
            )
            return
        except LeadEmailTooLarge as error:
            step = next(steps, None)
            if not paths or step is None:
                raise LeadEmailTooLarge(
                    'Lead email still exceeds its size budget after photo compression; review the saved lead.'
                ) from error
            logger.info('Lead %s: reducing saved photos to at most %s pixels, JPEG quality %s.',
                        lead.pk, step[0], step[1])
            _recompress_photos(lead, owned, max_dimension=step[0], quality=step[1])


def queue_lead_emails(queryset):
    """Queue an explicit admin resend, without disturbing active jobs."""
    return queryset.filter(
        Q(email_status__in=[LeadSubmission.STATUS_SENT, LeadSubmission.STATUS_FAILED])
        | Q(email_status=LeadSubmission.STATUS_PENDING, email_next_attempt_at__isnull=True)
    ).update(
        email_status=LeadSubmission.STATUS_PENDING,
        email_next_attempt_at=timezone.now(), email_attempts=0,
        email_claimed_at=None, email_claim_token=None, email_error='',
        updated_at=timezone.now(),
    )


def claim_next_lead():
    now = timezone.now()
    expired = Q(email_status=LeadSubmission.STATUS_SENDING, email_claimed_at__lt=now - CLAIM_TIMEOUT)
    # A worker killed on its final attempt must not leave the lead stuck forever.
    LeadSubmission.objects.filter(expired, email_attempts__gte=MAX_ATTEMPTS).update(
        email_status=LeadSubmission.STATUS_FAILED, email_next_attempt_at=None,
        email_claimed_at=None, email_claim_token=None,
        email_error='Email worker interrupted on final attempt; review before resending.',
        updated_at=now,
    )
    eligible = LeadSubmission.objects.filter(
        Q(email_status=LeadSubmission.STATUS_PENDING, email_next_attempt_at__lte=now) | expired,
        email_attempts__lt=MAX_ATTEMPTS,
    )
    lead_id = eligible.order_by('email_next_attempt_at', 'created_at', 'pk').values_list('pk', flat=True).first()
    if lead_id is None:
        return None
    token = uuid.uuid4()
    # Compare-and-set in one UPDATE. select_for_update() does not lock SQLite rows.
    if not eligible.filter(pk=lead_id).update(
        email_status=LeadSubmission.STATUS_SENDING, email_claimed_at=now,
        email_claim_token=token, email_next_attempt_at=None,
        email_attempts=F('email_attempts') + 1, updated_at=now,
    ):
        return None
    return LeadSubmission.objects.get(pk=lead_id, email_claim_token=token)


def is_temporary_email_error(error):
    if isinstance(error, SMTPAuthenticationError):
        return False
    if isinstance(error, SMTPRecipientsRefused):
        return bool(error.recipients) and all(400 <= result[0] < 500 for result in error.recipients.values())
    if isinstance(error, SMTPResponseException):
        return 400 <= error.smtp_code < 500
    if isinstance(error, (FileNotFoundError, PermissionError, ValueError)):
        return False
    return isinstance(error, (SMTPException, OSError))


def deliver_claimed_lead(lead):
    # Never let a previous worker overwrite a newer claim's result.
    owned = LeadSubmission.objects.filter(
        pk=lead.pk, email_status=LeadSubmission.STATUS_SENDING,
        email_claim_token=lead.email_claim_token,
    )
    if not owned.exists():
        return
    try:
        _send_with_size_fallback(lead, owned)
    except LeadClaimLost:
        return
    except Exception as error:
        retry = is_temporary_email_error(error) and lead.email_attempts < MAX_ATTEMPTS
        now = timezone.now()
        owned.update(
            email_status=LeadSubmission.STATUS_PENDING if retry else LeadSubmission.STATUS_FAILED,
            email_error=str(error)[:2000],
            email_next_attempt_at=now + timedelta(seconds=RETRY_DELAYS[lead.email_attempts - 1]) if retry else None,
            email_claimed_at=None, email_claim_token=None, updated_at=now,
        )
        logger.warning('Lead %s email attempt %s: %s (%s).', lead.pk, lead.email_attempts,
                       'retry scheduled' if retry else 'failed; needs attention', type(error).__name__)
    else:
        now = timezone.now()
        owned.update(
            email_status=LeadSubmission.STATUS_SENT, email_error='', emailed_at=now,
            email_next_attempt_at=None, email_claimed_at=None, email_claim_token=None,
            updated_at=now,
        )
        logger.info('Lead %s email accepted by SMTP server.', lead.pk)


def process_next_lead_email():
    lead = claim_next_lead()
    if lead is None:
        return False
    deliver_claimed_lead(lead)
    return True
