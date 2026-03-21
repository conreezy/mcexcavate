from django.core.management.base import BaseCommand

from gallery.models import GalleryImages, _build_gallery_thumbnail


class Command(BaseCommand):
    help = "Generate stored thumbnail files for gallery detail images."

    def add_arguments(self, parser):
        parser.add_argument(
            '--slug',
            action='append',
            dest='slugs',
            default=[],
            help='Limit processing to one or more gallery slugs. Repeat the flag to target multiple galleries.',
        )
        parser.add_argument(
            '--overwrite',
            action='store_true',
            help='Regenerate thumbnails even when a thumbnail file already exists.',
        )

    def handle(self, *args, **options):
        slugs = options['slugs']
        overwrite = options['overwrite']

        queryset = GalleryImages.objects.select_related('gallery').exclude(images='').exclude(images__isnull=True).order_by('id')
        if slugs:
            queryset = queryset.filter(gallery__slug__in=slugs)

        processed = 0
        updated = 0
        skipped = 0

        for gallery_image in queryset:
            processed += 1

            if gallery_image.thumbnail and not overwrite:
                skipped += 1
                continue

            gallery_image.thumbnail = _build_gallery_thumbnail(gallery_image.images)
            gallery_image.save(update_fields=['thumbnail'])
            updated += 1
            self.stdout.write(f"GalleryImages {gallery_image.id}: thumbnail generated")

        self.stdout.write(
            self.style.SUCCESS(
                f'Finished thumbnail generation. Processed={processed}, Updated={updated}, Skipped={skipped}'
            )
        )
