from django.urls import path, re_path
from django.views.generic import RedirectView

from .views import (
    gallery_delete_view,
    gallery_detail_view,
    gallery_edit_view,
    gallery_list_view,
)

app_name = "gallery"

urlpatterns = [
    path('', gallery_list_view, name='list'),
    path('<str:slug>/add-photo/', gallery_edit_view, name='add_photo'),
    path('<str:slug>/delete/', gallery_delete_view, name='delete'),
    path('<str:slug>/', gallery_detail_view, name='detail'),
    re_path(r'^(?P<slug>[^/]+)/add-photo$', RedirectView.as_view(pattern_name='gallery:add_photo', permanent=True)),
    re_path(r'^(?P<slug>[^/]+)/delete$', RedirectView.as_view(pattern_name='gallery:delete', permanent=True)),
    re_path(r'^(?P<slug>[^/]+)$', RedirectView.as_view(pattern_name='gallery:detail', permanent=True)),
]
