from django.contrib.sitemaps import Sitemap 
from django.urls import reverse

from gallery.models import Gallery

class GallerySitemap(Sitemap):

	def items(self):
		return Gallery.objects.all()


class StaticViewSitemap(Sitemap):

	def items(self):
		return ['home', 
				'excavation', 
				'interlock', 
				're-sodding',
				'maintenance',
				'careers',
				'about',
				'contact']

	def location(self, item):
		return reverse(item)