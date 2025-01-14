from django.urls import path
from AR.views import ImageTo3DView

urlpatterns = [
    path('convert/', ImageTo3DView.as_view(), name='convert_to_3d'),
]