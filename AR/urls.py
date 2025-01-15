from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_image, name='upload_image'),
    path('image/<int:image_id>/', views.view_image, name='view_image'),
]