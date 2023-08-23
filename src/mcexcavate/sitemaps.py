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
				'excavation', 
				'interlock', 
				'sod-installation',
				'concrete',
				'stamped_driveway_page',
           		'stamped_patio_page',
           		'stamped_walkway_page',
           		'concrete_repairs_page',
           		'concrete_sealing_page',
           		'concrete_steps_page',
           		'concrete_slabs_page',
				'careers',
				'about',
				'contact']

	def location(self, item):
		return reverse(item)