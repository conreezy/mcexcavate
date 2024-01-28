from django.conf import settings
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, re_path, include

from gallery.views import (
    gallery_create_view,
)

from .views import (
    home_page,

    #services
    services_page,
    excavation_page,
    interlock_page,
    re_sodding_page,
    stamped_concrete_page,
    concrete_repairs_page,
    concrete_resurfacing_page,
    concrete_sealing_page,
    concrete_steps_page,
    concrete_slabs_page,
    parging_page,

    #form fill
    concrete_success_page,

    #about
    careers_page,
    about_page,
    contact_page,

    # backend
    DashboardView,
)

from blog.views import (
    blog_post_create_view,
    #blog_sitemap,
)

from .sitemaps import GallerySitemap, BlogSitemap, StaticViewSitemap

sitemaps = {
    "static":StaticViewSitemap,
    "galleries":GallerySitemap,
    "blogs":BlogSitemap 
}

urlpatterns = [
    path('', home_page, name='home'),

    # -- Services
    path('services/', services_page, name='services'),
    path('excavation/', excavation_page, name='excavation'),
    path('interlock/', interlock_page, name='interlock'),
    path('sod-installation/', re_sodding_page, name='sod-installation'),
    path('concrete/', stamped_concrete_page, name='concrete'),
    path('concrete-repair/', concrete_repairs_page, name='concrete_repairs_page'),
    path('concrete-resurfacing/', concrete_resurfacing_page, name='concrete_resurfacing_page'),
    path('concrete-sealing/', concrete_sealing_page, name='concrete_sealing_page'),
    path('concrete-steps/', concrete_steps_page, name='concrete_steps_page'),
    path('concrete-slabs/', concrete_slabs_page, name='concrete_slabs_page'),
    path('parging/', parging_page, name='parging'),
    path('concrete/success/', concrete_success_page, name='concrete_success_page'),

    # -- Gallery 
    path('gallery-new', gallery_create_view),
    path('gallery/', include('gallery.urls')),
    
    # -- Blog
    path('blog-new', blog_post_create_view),
    path('blog/', include('blog.urls')),

    # -- Other pages
    path('careers/', careers_page, name='careers'),
    path('about/', about_page, name='about'),
    path('contact/', contact_page, name='contact'),

    # -- Admin pages
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    
    path('admin/', admin.site.urls),

    # -- Sitemap
    path('sitemap.xml', sitemap, {"sitemaps":sitemaps}),

    # -- CkEditor
    path('ckeditor', include('ckeditor_uploader.urls')),
]

if settings.DEBUG:
    # Test Mode
    from django.conf.urls.static import static
    #urlpatterns += static_urlpatterns()
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,  document_root=settings.MEDIA_ROOT)