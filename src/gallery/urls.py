from django.urls import path

from .views import (
    gallery_list_view,
    gallery_detail_view,
    gallery_edit_view,
    gallery_delete_view,
    )

urlpatterns = [
    path('', gallery_list_view),
    path('<str:slug>', gallery_detail_view),
    path('<str:slug>/add-photo/', gallery_edit_view),
    path('<str:slug>/delete/', gallery_delete_view),
]