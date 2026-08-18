from unittest.mock import patch

from io import BytesIO
from smtplib import SMTPAuthenticationError
from tempfile import TemporaryDirectory

from captcha.client import RecaptchaResponse
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.test import TestCase
from django.urls import reverse
from PIL import Image

from mcexcavate.forms import ContactPageContactForm, ServicePageContactForm
from mcexcavate.views import LEAD_EMAIL_RECIPIENTS, send_email_with_attachments
from project.models import LeadSubmission, LeadSubmissionImage


class CorePageTests(TestCase):
    def _valid_contact_data(self):
        return {
            'name': 'Test Lead',
            'email': 'lead@example.com',
            'phone': '+16136087722',
            'address': '123 Test Street',
            'service': 'Stamped Concrete',
            'content': 'Need a quote for a walkway.',
            'marketing': 'Google Search',
            'captcha': 'test-token',
        }

    def _make_uploaded_image(self, name='project.jpg', size=(10, 10), color='white'):
        file_obj = BytesIO()
        image = Image.new('RGB', size, color=color)
        image.save(file_obj, format='JPEG')
        file_obj.seek(0)
        return SimpleUploadedFile(name, file_obj.read(), content_type='image/jpeg')

    def test_key_pages_load(self):
        pages = [
            reverse('home'),
            reverse('services'),
            reverse('concrete'),
            reverse('concrete_services_page'),
            reverse('contact'),
            reverse('about'),
            reverse('careers'),
            reverse('excavation'),
            reverse('bollards'),
        ]

        for url in pages:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_contact_forms_render_multi_file_input(self):
        for form_class in (ContactPageContactForm, ServicePageContactForm):
            with self.subTest(form=form_class.__name__):
                rendered = str(form_class()['images'])
                self.assertIn('multiple', rendered)

    @patch('mcexcavate.views.send_email_with_attachments')
    @patch('captcha.fields.client.submit')
    def test_contact_form_submission_redirects_and_sends_email(self, mock_submit, mock_send_email):
        mock_submit.return_value = RecaptchaResponse(True, extra_data={'score': 0.9})

        response = self.client.post(reverse('contact'), data=self._valid_contact_data())

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/contact/#contactform')
        mock_send_email.assert_called_once()
        self.assertEqual(LeadSubmission.objects.count(), 1)
        self.assertEqual(LeadSubmission.objects.get().email_status, LeadSubmission.STATUS_SENT)

    @patch('mcexcavate.views.send_email_with_attachments')
    @patch('captcha.fields.client.submit')
    def test_contact_form_handles_email_delivery_failure_without_server_error(self, mock_submit, mock_send_email):
        mock_submit.return_value = RecaptchaResponse(True, extra_data={'score': 0.9})
        mock_send_email.side_effect = SMTPAuthenticationError(535, b'Authentication failed')

        response = self.client.post(reverse('contact'), data=self._valid_contact_data(), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Your information was received')
        self.assertEqual(LeadSubmission.objects.count(), 1)
        self.assertEqual(LeadSubmission.objects.get().email_status, LeadSubmission.STATUS_FAILED)

    @patch('mcexcavate.views.send_email_with_attachments')
    @patch('captcha.fields.client.submit')
    def test_service_page_form_submissions_redirect_and_send_email(self, mock_submit, mock_send_email):
        mock_submit.return_value = RecaptchaResponse(True, extra_data={'score': 0.9})
        service_pages = [
            ('concrete', 'Stamped Concrete', '/concrete/#contactform'),
            ('concrete_slabs_page', 'Concrete Slabs', '/concrete-slabs/#contactform'),
            ('concrete_steps_page', 'Concrete Steps', '/concrete-steps/#contactform'),
            ('concrete_repairs_page', 'Concrete Repairs', '/concrete-repair/#contactform'),
            ('concrete_resurfacing_page', 'Concrete Resurfacing', '/concrete-resurfacing/#contactform'),
            ('excavation', 'Excavation', '/excavation/#contactform'),
            ('bollards', 'Bollards', '/bollards/#contactform'),
        ]

        for url_name, service, redirect_url in service_pages:
            with self.subTest(url_name=url_name, service=service):
                mock_send_email.reset_mock()
                response = self.client.post(
                    reverse(url_name),
                    data={**self._valid_contact_data(), 'service': service},
                )

                self.assertEqual(response.status_code, 302)
                self.assertEqual(response['Location'], redirect_url)
                mock_send_email.assert_called_once()


    @patch('mcexcavate.views.send_email_with_attachments')
    @patch('captcha.fields.client.submit')
    def test_contact_form_accepts_five_valid_uploaded_images(self, mock_submit, mock_send_email):
        mock_submit.return_value = RecaptchaResponse(True, extra_data={'score': 0.9})
        upload_files = [self._make_uploaded_image(name=f'project-{index}.jpg') for index in range(5)]

        with TemporaryDirectory() as temp_media:
            with self.settings(MEDIA_ROOT=temp_media):
                response = self.client.post(
                    reverse('contact'),
                    data={**self._valid_contact_data(), 'images': upload_files},
                )

                self.assertEqual(LeadSubmissionImage.objects.count(), 5)
                for lead_image in LeadSubmissionImage.objects.all():
                    self.assertTrue(lead_image.file.storage.exists(lead_image.file.name))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/contact/#contactform')
        mock_send_email.assert_called_once()

    @patch('mcexcavate.views.send_email_with_attachments')
    @patch('captcha.fields.client.submit')
    def test_contact_form_rejects_invalid_uploaded_image_with_specific_error(self, mock_submit, mock_send_email):
        mock_submit.return_value = RecaptchaResponse(True, extra_data={'score': 0.9})
        invalid_file = SimpleUploadedFile('not-an-image.txt', b'not really an image', content_type='text/plain')

        response = self.client.post(
            reverse('contact'),
            data={**self._valid_contact_data(), 'images': invalid_file},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'There was an error in your form submission. Please check the fields and try again.')
        self.assertContains(response, 'not-an-image.txt')
        self.assertContains(response, 'The file is not a valid image.')
        mock_send_email.assert_not_called()

    @patch('mcexcavate.views.send_email_with_attachments')
    @patch('captcha.fields.client.submit')
    def test_contact_form_rejects_more_than_maximum_images(self, mock_submit, mock_send_email):
        mock_submit.return_value = RecaptchaResponse(True, extra_data={'score': 0.9})
        upload_files = [self._make_uploaded_image(name=f'project-{index}.jpg') for index in range(6)]

        response = self.client.post(
            reverse('contact'),
            data={**self._valid_contact_data(), 'images': upload_files},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'You can upload up to 5 images, but you selected 6.')
        mock_send_email.assert_not_called()

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_lead_email_is_addressed_to_all_recipients(self):
        send_email_with_attachments(self._valid_contact_data(), [], 'Excavation')

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, LEAD_EMAIL_RECIPIENTS)
