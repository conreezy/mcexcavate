from unittest.mock import patch

from io import BytesIO

from captcha.client import RecaptchaResponse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from PIL import Image

from mcexcavate.forms import ContactPageContactForm, ServicePageContactForm


class CorePageTests(TestCase):
    def _valid_contact_data(self):
        return {
            'name': 'Test Lead',
            'email': 'lead@example.com',
            'phone': '+16136087722',
            'address': '123 Test Street',
            'service': 'Concrete',
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

    @patch('mcexcavate.views.send_email_with_attachments')
    @patch('captcha.fields.client.submit')
    def test_service_page_form_submission_redirects_and_sends_email(self, mock_submit, mock_send_email):
        mock_submit.return_value = RecaptchaResponse(True, extra_data={'score': 0.9})

        response = self.client.post(reverse('concrete'), data=self._valid_contact_data())

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/concrete/#contactform')
        mock_send_email.assert_called_once()


    @patch('mcexcavate.views.send_email_with_attachments')
    @patch('captcha.fields.client.submit')
    def test_contact_form_accepts_five_valid_uploaded_images(self, mock_submit, mock_send_email):
        mock_submit.return_value = RecaptchaResponse(True, extra_data={'score': 0.9})
        upload_files = [self._make_uploaded_image(name=f'project-{index}.jpg') for index in range(5)]

        response = self.client.post(
            reverse('contact'),
            data={**self._valid_contact_data(), 'images': upload_files},
        )

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
