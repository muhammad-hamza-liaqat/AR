# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from django.conf import settings
# import os
# import torch
# from torchvision.transforms import Compose, Resize, ToTensor, Normalize
# from PIL import Image
# import numpy as np
# import cv2
# import open3d as o3d  # Import Open3D for creating 3D models
# from .serializers import ImageSerializer

# class ImageTo3DView(APIView):
#     def post(self, request, *args, **kwargs):
#         serializer = ImageSerializer(data=request.data)
#         if serializer.is_valid():
#             image = serializer.validated_data['image']
#             original_image_path = self.save_image(image)

#             depth_map = self.generate_depth_map(original_image_path)

#             three_d_model_path = self.save_as_3d_model(depth_map, original_image_path)

#             return Response({
#                 "message": "3D model created successfully.",
#                 "original_image_url": f"{settings.MEDIA_URL}original/{os.path.basename(original_image_path)}",
#                 "three_d_model_url": f"{settings.MEDIA_URL}3d/{os.path.basename(three_d_model_path)}",
#             }, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def save_image(self, image):
#         save_dir = os.path.join(settings.MEDIA_ROOT, 'original')
#         os.makedirs(save_dir, exist_ok=True)
#         save_path = os.path.join(save_dir, image.name)
#         with open(save_path, 'wb') as f:
#             for chunk in image.chunks():
#                 f.write(chunk)
#         return save_path

#     def generate_depth_map(self, image_path):
#         model = torch.hub.load("intel-isl/MiDaS", "DPT_Large", pretrained=True)
#         model.eval()

#         transform = Compose([
#             Resize((384, 384)),  # Resize for the model input
#             ToTensor(),
#             Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]),
#         ])

#         img = Image.open(image_path).convert("RGB")
#         input_tensor = transform(img).unsqueeze(0)

#         with torch.no_grad():
#             depth_map = model(input_tensor).squeeze().cpu().numpy()

#         depth_map = (depth_map - depth_map.min()) / (depth_map.max() - depth_map.min())
#         return depth_map

#     def save_as_3d_model(self, depth_map, original_image_path):
#         save_dir = os.path.join(settings.MEDIA_ROOT, '3d')
#         os.makedirs(save_dir, exist_ok=True)
#         model_name = f"3d_{os.path.basename(original_image_path).split('.')[0]}.ply"
#         model_path = os.path.join(save_dir, model_name)

#         h, w = depth_map.shape
#         x, y = np.meshgrid(np.arange(w), np.arange(h))
#         z = depth_map  # Depth map values

#         points = np.stack((x.flatten(), y.flatten(), z.flatten()), axis=1)

#         point_cloud = o3d.geometry.PointCloud()
#         point_cloud.points = o3d.utility.Vector3dVector(points)

#         o3d.io.write_point_cloud(model_path, point_cloud)
#         return model_path


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import os
import torch
from torchvision.transforms import Compose, Resize, ToTensor, Normalize
from PIL import Image
import numpy as np
import cv2
import trimesh 
from .serializers import ImageSerializer

class ImageTo3DView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ImageSerializer(data=request.data)
        if serializer.is_valid():
            image = serializer.validated_data['image']
            original_image_path = self.save_image(image)

            depth_map = self.generate_depth_map(original_image_path)

            three_d_model_path = self.save_as_3d_model(depth_map, original_image_path)

            return Response({
                "message": "3D model created successfully.",
                "original_image_url": f"{settings.MEDIA_URL}original/{os.path.basename(original_image_path)}",
                "three_d_model_url": f"{settings.MEDIA_URL}3d/{os.path.basename(three_d_model_path)}",
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def save_image(self, image):
        save_dir = os.path.join(settings.MEDIA_ROOT, 'original')
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, image.name)
        with open(save_path, 'wb') as f:
            for chunk in image.chunks():
                f.write(chunk)
        return save_path

    def generate_depth_map(self, image_path):
        model = torch.hub.load("intel-isl/MiDaS", "DPT_Large", pretrained=True)
        model.eval()

        transform = Compose([
            Resize((384, 384)),
            ToTensor(),
            Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]),
        ])

        img = Image.open(image_path).convert("RGB")
        input_tensor = transform(img).unsqueeze(0)

        with torch.no_grad():
            depth_map = model(input_tensor).squeeze().cpu().numpy()

        depth_map = (depth_map - depth_map.min()) / (depth_map.max() - depth_map.min())
        return depth_map

    def save_as_3d_model(self, depth_map, original_image_path):
        save_dir = os.path.join(settings.MEDIA_ROOT, '3d')
        os.makedirs(save_dir, exist_ok=True)
        model_name = f"3d_{os.path.basename(original_image_path).split('.')[0]}.glb"
        model_path = os.path.join(save_dir, model_name)

        img = np.array(Image.open(original_image_path).resize(depth_map.shape[::-1]))

        h, w = depth_map.shape
        x, y = np.meshgrid(np.arange(w), np.arange(h))
        z = depth_map

        vertices = np.stack((x.flatten(), y.flatten(), z.flatten()), axis=1)

        faces = []
        for i in range(h - 1):
            for j in range(w - 1):
                idx = i * w + j
                faces.append([idx, idx + 1, idx + w])
                faces.append([idx + 1, idx + w + 1, idx + w])

        faces = np.array(faces)

        mesh = trimesh.Trimesh(vertices=vertices, faces=faces, vertex_colors=img.reshape(-1, 3))

        mesh.export(model_path)
        return model_path

