from django.conf import settings
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path, re_path
from django.views.generic import RedirectView

from gallery.views import gallery_create_view

from .sitemaps import BlogSitemap, GallerySitemap, StaticViewSitemap
from .views import (
    DashboardView,
    about_page,
    bollard_page,
    careers_page,
    concrete_repairs_page,
    concrete_resurfacing_page,
    concrete_services_page,
    concrete_slabs_page,
    concrete_steps_page,
    concrete_success_page,
    contact_page,
    excavation_page,
    home_page,
    services_page,
    stamped_concrete_page,
)
from blog.views import blog_post_create_view

sitemaps = {
    'static': StaticViewSitemap,
    'galleries': GallerySitemap,
    'blogs': BlogSitemap,
}

urlpatterns = [
    path('', home_page, name='home'),

    path('services/', services_page, name='services'),
    path('concrete-services/', concrete_services_page, name='concrete_services_page'),
    path('concrete/', stamped_concrete_page, name='concrete'),
    path('concrete-repair/', concrete_repairs_page, name='concrete_repairs_page'),
    path('concrete-resurfacing/', concrete_resurfacing_page, name='concrete_resurfacing_page'),
    path('concrete-steps/', concrete_steps_page, name='concrete_steps_page'),
    path('concrete-slabs/', concrete_slabs_page, name='concrete_slabs_page'),
    path('excavation/', excavation_page, name='excavation'),
    path('bollards/', bollard_page, name='bollards'),
    path('concrete/success/', concrete_success_page, name='concrete_success_page'),

    path('gallery-new/', gallery_create_view, name='gallery_create'),
    re_path(r'^gallery-new$', RedirectView.as_view(pattern_name='gallery_create', permanent=True)),
    path('gallery/', include(('gallery.urls', 'gallery'), namespace='gallery')),

    path('blog-new/', blog_post_create_view, name='blog_create'),
    re_path(r'^blog-new$', RedirectView.as_view(pattern_name='blog_create', permanent=True)),
    path('blog/', include(('blog.urls', 'blog'), namespace='blog')),

    path('careers/', careers_page, name='careers'),
    path('about/', about_page, name='about'),
    path('contact/', contact_page, name='contact'),

    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('admin/', admin.site.urls),

    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}),

    path('ckeditor/', include('ckeditor_uploader.urls')),
    re_path(r'^ckeditor$', RedirectView.as_view(url='/ckeditor/', permanent=True)),
]

if settings.DEBUG:
    from django.conf.urls.static import static

    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
