from django.conf import settings
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, re_path, include

from gallery.views import (
    gallery_create_view,
    )

from .views import (
    home_page,

    excavation_page,
    interlock_page,
    re_sodding_page,
    maintenance_page,
    concrete_page,
    parging_page,
    asphalt_page,
    asphalt_repairs_page,

    careers_page,
    about_page,
    contact_page,
    DashboardView,
)

from .sitemaps import GallerySitemap, StaticViewSitemap

sitemaps = {
    "static":StaticViewSitemap,
    "galleries":GallerySitemap   
}

urlpatterns = [
    path('', home_page, name='home'),

    path('gallery-new/', gallery_create_view),
    path('gallery/', include('gallery.urls')),

    # -- Services
    path('excavation/', excavation_page, name='excavation'),
    path('interlock/', interlock_page, name='interlock'),
    path('sod-installation/', re_sodding_page, name='sod-installation'),
    path('lawn-mowing/', maintenance_page, name='lawn-mowing'),
    path('concrete/', concrete_page, name='concrete'),
    path('parging/', parging_page, name='parging'),
    path('asphalt-paving/', asphalt_page, name='asphalt-paving'),
    path('asphalt-repairs/', asphalt_repairs_page, name='asphalt-repairs'),
    
    # 
    path('careers/', careers_page, name='careers'),
    path('about/', about_page, name='about'),
    path('contact/', contact_page, name='contact'),

    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    
    path('admin/', admin.site.urls),

    path('sitemap.xml', sitemap, {"sitemaps":sitemaps})
]

if settings.DEBUG:
    # Test Mode
    from django.conf.urls.static import static
    #urlpatterns += static_urlpatterns()
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,  document_root=settings.MEDIA_ROOT)