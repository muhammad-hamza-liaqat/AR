# convert3d/utils.py
import trimesh
import numpy as np
from PIL import Image

def create_textured_3d_mesh(image_path, output_path):
    # Open the image and get dimensions
    img = Image.open(image_path)
    width, height = img.size
    texture = np.array(img) / 255.0  # Normalize texture
    
    # Create a grid of vertices
    x = np.linspace(0, 1, width)
    y = np.linspace(0, 1, height)
    xv, yv = np.meshgrid(x, y)
    zv = np.zeros_like(xv)  # Flat surface (z = 0)

    # Combine into vertices
    vertices = np.stack([xv.flatten(), yv.flatten(), zv.flatten()], axis=1)

    # Create triangular faces
    faces = []
    for i in range(height - 1):
        for j in range(width - 1):
            top_left = i * width + j
            top_right = top_left + 1
            bottom_left = top_left + width
            bottom_right = bottom_left + 1

            faces.append([top_left, bottom_left, top_right])
            faces.append([top_right, bottom_left, bottom_right])

    faces = np.array(faces)

    # Create mesh and apply texture
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
    mesh.visual.vertex_colors = texture.reshape(-1, 3)  # Apply texture

    # Export to .glb
    mesh.export(output_path)

# changes added