import time

from django.core.management.base import BaseCommand, CommandError

from gallery.ai_alt_text import AltTextGenerationError, generate_alt_text_for_image_file
from gallery.models import Gallery, GalleryImages


class Command(BaseCommand):
    help = "Generate AI alt text for gallery cover images and gallery detail images."

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=None, help='Process at most this many records per model.')
        parser.add_argument('--model', default=None, help='Override the default OpenAI model.')
        parser.add_argument('--detail', default=None, help='Override image detail level, for example high or low.')
        parser.add_argument('--dry-run', action='store_true', help='Preview alt text without saving it.')
        parser.add_argument('--gallery-only', action='store_true', help='Process only Gallery cover images.')
        parser.add_argument('--gallery-images-only', action='store_true', help='Process only GalleryImages records.')
        parser.add_argument('--sleep', type=float, default=0.0, help='Optional delay between requests in seconds.')

    def handle(self, *args, **options):
        if options['gallery_only'] and options['gallery_images_only']:
            raise CommandError('Choose either --gallery-only or --gallery-images-only, not both.')

        model = options['model']
        detail = options['detail']
        dry_run = options['dry_run']
        limit = options['limit']
        sleep_seconds = options['sleep']

        total_processed = 0
        total_updated = 0
        total_failed = 0

        if not options['gallery_images_only']:
            processed, updated, failed = self._process_galleries(limit, model, detail, dry_run, sleep_seconds)
            total_processed += processed
            total_updated += updated
            total_failed += failed

        if not options['gallery_only']:
            processed, updated, failed = self._process_gallery_images(limit, model, detail, dry_run, sleep_seconds)
            total_processed += processed
            total_updated += updated
            total_failed += failed

        self.stdout.write(
            self.style.SUCCESS(
                f'Finished AI alt-text generation. Processed={total_processed}, Updated={total_updated}, Failed={total_failed}'
            )
        )

    def _process_galleries(self, limit, model, detail, dry_run, sleep_seconds):
        queryset = Gallery.objects.exclude(image='').exclude(image__isnull=True).order_by('id')
        if limit:
            queryset = queryset[:limit]

        processed = updated = failed = 0
        for gallery in queryset:
            processed += 1
            try:
                alt_text = generate_alt_text_for_image_file(gallery.image, model=model, detail=detail)
                self.stdout.write(f"Gallery {gallery.id}: {alt_text}")
                if not dry_run:
                    gallery.image_alt = alt_text
                    gallery.save(update_fields=['image_alt'])
                    updated += 1
            except AltTextGenerationError as exc:
                failed += 1
                self.stderr.write(self.style.ERROR(f'Gallery {gallery.id} failed: {exc}'))
            if sleep_seconds:
                time.sleep(sleep_seconds)
        return processed, updated, failed

    def _process_gallery_images(self, limit, model, detail, dry_run, sleep_seconds):
        queryset = GalleryImages.objects.exclude(images='').exclude(images__isnull=True).order_by('id')
        if limit:
            queryset = queryset[:limit]

        processed = updated = failed = 0
        for image in queryset:
            processed += 1
            try:
                alt_text = generate_alt_text_for_image_file(image.images, model=model, detail=detail)
                self.stdout.write(f"GalleryImages {image.id}: {alt_text}")
                if not dry_run:
                    image.alt = alt_text
                    image.save(update_fields=['alt'])
                    updated += 1
            except AltTextGenerationError as exc:
                failed += 1
                self.stderr.write(self.style.ERROR(f'GalleryImages {image.id} failed: {exc}'))
            if sleep_seconds:
                time.sleep(sleep_seconds)
        return processed, updated, failed
