from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from .models import BlogPost, Concrete


class BlogPublishingTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='secret123')

    def test_published_manager_excludes_future_posts(self):
        published_post = BlogPost.objects.create(
            user=self.user,
            title='Published Post',
            slug='published-post',
            content='Visible content',
            service=Concrete,
            publish_date=timezone.now() - timedelta(days=1),
        )
        BlogPost.objects.create(
            user=self.user,
            title='Future Post',
            slug='future-post',
            content='Hidden content',
            service=Concrete,
            publish_date=timezone.now() + timedelta(days=1),
        )

        published = list(BlogPost.objects.published())

        self.assertEqual(published, [published_post])

    def test_blog_list_only_shows_published_posts(self):
        BlogPost.objects.create(
            user=self.user,
            title='Visible Post',
            slug='visible-post',
            content='Visible content',
            service=Concrete,
            publish_date=timezone.now() - timedelta(days=1),
        )
        BlogPost.objects.create(
            user=self.user,
            title='Hidden Post',
            slug='hidden-post',
            content='Hidden content',
            service=Concrete,
            publish_date=timezone.now() + timedelta(days=1),
        )

        response = self.client.get('/blog/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Visible Post')
        self.assertNotContains(response, 'Hidden Post')
