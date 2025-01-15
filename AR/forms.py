# convert3d/forms.py
from django import forms
from .models import Image3D

class Image3DForm(forms.ModelForm):
    class Meta:
        model = Image3D
        fields = ['original_image']
