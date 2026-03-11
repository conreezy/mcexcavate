from django.urls import path, re_path
from django.views.generic import RedirectView

from .views import (
    blog_post_delete_view,
    blog_post_detail_view,
    blog_post_list_view,
    blog_post_update_view,
)

app_name = "blog"

urlpatterns = [
    path('', blog_post_list_view, name='list'),
    path('<str:slug>/edit/', blog_post_update_view, name='edit'),
    path('<str:slug>/delete/', blog_post_delete_view, name='delete'),
    path('<str:slug>/', blog_post_detail_view, name='detail'),
    re_path(r'^(?P<slug>[^/]+)/edit$', RedirectView.as_view(pattern_name='blog:edit', permanent=True)),
    re_path(r'^(?P<slug>[^/]+)/delete$', RedirectView.as_view(pattern_name='blog:delete', permanent=True)),
    re_path(r'^(?P<slug>[^/]+)$', RedirectView.as_view(pattern_name='blog:detail', permanent=True)),
]
