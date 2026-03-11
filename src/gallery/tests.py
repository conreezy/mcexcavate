from io import BytesIO
from unittest.mock import MagicMock
from unittest.mock import patch

import requests

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase
from PIL import Image

from .models import Gallery, GalleryImages, MAX_GALLERY_IMAGE_DIMENSION


def make_test_image(name='test.jpg', color='blue'):
    image = Image.new('RGB', (120, 80), color=color)
    buffer = BytesIO()
    image.save(buffer, format='JPEG')
    buffer.seek(0)
    return SimpleUploadedFile(name, buffer.read(), content_type='image/jpeg')


class GalleryAltTextTests(TestCase):
    @patch('gallery.models.generate_alt_text_for_image_file', return_value='stamped concrete patio with curved edge')
    def test_gallery_save_generates_cover_image_alt_text(self, mock_generate):
        gallery = Gallery.objects.create(
            title='Stamped Concrete',
            image=make_test_image('cover.jpg'),
            slug='stamped-concrete',
            description='Gallery description',
            meta_title='Stamped Concrete Projects',
            meta_keywords='concrete, patio',
        )

        self.assertEqual(gallery.image_alt, 'stamped concrete patio with curved edge')
        mock_generate.assert_called_once()

    @patch('gallery.models.generate_alt_text_for_image_file', return_value='close-up of stamped concrete walkway surface')
    def test_gallery_images_save_generates_alt_text(self, mock_generate):
        gallery = Gallery.objects.create(
            title='Stamped Concrete',
            image=make_test_image('cover.jpg'),
            slug='stamped-concrete',
            description='Gallery description',
            meta_title='Stamped Concrete Projects',
            meta_keywords='concrete, patio',
        )

        image = GalleryImages.objects.create(
            images=make_test_image('detail.jpg'),
            gallery=gallery,
        )

        self.assertEqual(image.alt, 'close-up of stamped concrete walkway surface')
        self.assertGreaterEqual(mock_generate.call_count, 1)

    @patch('gallery.management.commands.generate_ai_alt_text.generate_alt_text_for_image_file')
    @patch('gallery.models.generate_alt_text_for_image_file')
    def test_management_command_overwrites_existing_alt_text(self, mock_model_generate, mock_command_generate):
        mock_model_generate.side_effect = [
            'original cover alt text',
            'original detail alt text',
        ]
        gallery = Gallery.objects.create(
            title='Stamped Concrete',
            image=make_test_image('cover.jpg'),
            slug='stamped-concrete',
            description='Gallery description',
            meta_title='Stamped Concrete Projects',
            meta_keywords='concrete, patio',
        )
        detail_image = GalleryImages.objects.create(
            images=make_test_image('detail.jpg'),
            gallery=gallery,
        )

        gallery.image_alt = 'manual cover alt'
        gallery.save(update_fields=['image_alt'])
        detail_image.alt = 'manual detail alt'
        detail_image.save(update_fields=['alt'])

        mock_command_generate.side_effect = [
            'updated AI cover alt text',
            'updated AI detail alt text',
        ]

        call_command('generate_ai_alt_text')

        gallery.refresh_from_db()
        detail_image.refresh_from_db()

        self.assertEqual(gallery.image_alt, 'updated AI cover alt text')
        self.assertEqual(detail_image.alt, 'updated AI detail alt text')


class GalleryImageOptimizationTests(TestCase):
    @patch('gallery.models.generate_alt_text_for_image_file', return_value='optimized gallery cover image')
    def test_gallery_cover_image_is_converted_to_optimized_jpeg_with_max_dimension(self, mock_generate):
        large_image = Image.new('RGB', (3200, 2000), color='green')
        source = BytesIO()
        large_image.save(source, format='PNG')
        source.seek(0)
        upload = SimpleUploadedFile('large-cover.png', source.read(), content_type='image/png')

        gallery = Gallery.objects.create(
            title='Stamped Concrete',
            image=upload,
            slug='stamped-concrete',
            description='Gallery description',
            meta_title='Stamped Concrete Projects',
            meta_keywords='concrete, patio',
        )

        gallery.image.open('rb')
        with Image.open(gallery.image) as saved_image:
            self.assertEqual(saved_image.format, 'JPEG')
            self.assertLessEqual(max(saved_image.size), MAX_GALLERY_IMAGE_DIMENSION)

        self.assertTrue(gallery.image.name.endswith('.jpg'))
        mock_generate.assert_called_once()


class GalleryAltTextRetryTests(TestCase):
    @patch('gallery.ai_alt_text.time.sleep', return_value=None)
    @patch('gallery.ai_alt_text.requests.post')
    def test_generate_alt_text_retries_after_rate_limit(self, mock_post, mock_sleep):
        from gallery.ai_alt_text import generate_alt_text_for_image_file

        first_response = MagicMock()
        first_response.status_code = 429
        first_response.text = 'rate limited'
        first_response.raise_for_status.side_effect = requests.HTTPError('429')

        second_response = MagicMock()
        second_response.status_code = 200
        second_response.json.return_value = {
            'output': [
                {
                    'type': 'message',
                    'content': [
                        {'type': 'output_text', 'text': 'Stamped concrete patio beside brick house'}
                    ],
                }
            ]
        }
        second_response.raise_for_status.return_value = None

        mock_post.side_effect = [first_response, second_response]

        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            alt_text = generate_alt_text_for_image_file(make_test_image('retry.jpg'))

        self.assertEqual(alt_text, 'Stamped concrete patio beside brick house')
        self.assertEqual(mock_post.call_count, 2)
        mock_sleep.assert_called_once()
