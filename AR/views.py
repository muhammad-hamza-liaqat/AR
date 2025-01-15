from django.shortcuts import render, redirect, get_object_or_404
from .forms import Image3DForm
from .models import Image3D
from .utils import create_textured_3d_model
import os


def upload_image(request):
    if request.method == 'POST':
        form = Image3DForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save()

            # Paths
            input_image_path = image.original_image.path
            output_dir = os.path.join(os.path.dirname(input_image_path), "processed")
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"textured_model_{image.id}.glb")

            # Generate 3D model
            create_textured_3d_model(input_image_path, output_path, invert_y_axis=True)

            # Save the processed file path
            image.processed_image.name = f"processed/textured_model_{image.id}.glb"
            image.save()

            return redirect('view_image', image_id=image.id)
    else:
        form = Image3DForm()

    return render(request, 'AR/upload.html', {'form': form})


def view_image(request, image_id):
    image = get_object_or_404(Image3D, id=image_id)
    return render(request, 'AR/view_image.html', {'image': image})
