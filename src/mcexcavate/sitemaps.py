from django.contrib.sitemaps import Sitemap 
from django.urls import reverse

from gallery.models import Gallery
from blog.models import BlogPost

class GallerySitemap(Sitemap):
	def items(self):
		return Gallery.objects.all()
 
class BlogSitemap(Sitemap):
	def items(self):
		return BlogPost.objects.all()


class StaticViewSitemap(Sitemap):

	def items(self):
		return ['home',
				'services', 
				'concrete',
				'concrete_slabs_page',
				'concrete_steps_page',
				'concrete_repairs_page',
				'concrete_resurfacing_page',
				'concrete_sealing_page',
				'parging',
				'sod-installation',
				'interlock', 
				'excavation', 
				'bollards',
				'about',
				'careers',
				'contact']

	def location(self, item):
		return reverse(item)