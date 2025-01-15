# convert3d/views.py
from django.shortcuts import render, redirect
from .forms import Image3DForm
from .models import Image3D
from .utils import create_textured_3d_mesh
import os

def upload_image(request):
    if request.method == 'POST':
        form = Image3DForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save()

            # Paths
            input_path = image.original_image.path
            output_path = os.path.join(os.path.dirname(input_path), f"textured_3d_model_{image.id}.glb")

            # Call the function without extra arguments
            create_textured_3d_mesh(input_path, output_path)

            # Save the .glb file path
            image.processed_image.name = f"images/processed/textured_3d_model_{image.id}.glb"
            image.save()

            return redirect('view_image', image_id=image.id)
    else:
        form = Image3DForm()

    return render(request, 'AR/upload.html', {'form': form})

def view_image(request, image_id):
    image = Image3D.objects.get(id=image_id)
    return render(request, 'AR/view_image.html', {'image': image})
