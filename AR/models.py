# convert3d/models.py
from django.db import models

class Image3D(models.Model):
    original_image = models.ImageField(upload_to='images/')
    processed_image = models.ImageField(upload_to='images/', blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image {self.id}"
