import trimesh
import numpy as np
from PIL import Image


def create_textured_3d_model(image_path, output_path, invert_y_axis=False, depth_map=None, depth_scale=0.1):
    """
    Generate a 3D GLB model from an image with optional depth mapping.
    Args:
        image_path (str): Path to the input image.
        output_path (str): Path to save the 3D model.
        invert_y_axis (bool): Whether to invert the Y-axis (corrects for orientation in some viewers).
        depth_map (str): Path to an optional depth map for Z-axis variations.
        depth_scale (float): Scale for depth variations (ignored if depth_map is None).
    """
    # Load the image and process it
    img = Image.open(image_path).convert("RGBA")
    width, height = img.size
    texture = np.array(img) / 255.0  # Normalize texture

    # Create grid of vertices
    x = np.linspace(0, 1, width)
    y = np.linspace(0, 1, height)
    xv, yv = np.meshgrid(x, y)
    zv = np.zeros_like(xv)  # Flat Z-plane

    # Optional depth mapping
    if depth_map:
        depth_img = Image.open(depth_map).convert("L")
        depth_array = np.array(depth_img) / 255.0
        zv = depth_array * depth_scale

    # Invert Y-axis if needed
    if invert_y_axis:
        yv = 1 - yv

    # Combine vertices
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
    mesh.visual.vertex_colors = texture.reshape(-1, 4)

    # Export model to GLTF/GLB
    mesh.export(output_path)
    return output_path
