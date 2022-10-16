import time
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from django.conf import settings
from django.shortcuts import render, reverse
from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Upload, OrthoImage, TileImage
from .utils import create_image_object, tile_creating_function, get_policy


class UploadView(LoginRequiredMixin, CreateView):
    model = Upload
    fields = ['name', 'image']

    def get_context_data(self, **kwargs):
        context_data = super(UploadView, self).get_context_data(**kwargs)
        return context_data


class FilePolicyAPI(APIView):

    def post(self, request, *args, **kwargs):
        """
        The initial post request includes the filename
        and auth credentials. In our case, we'll use
        Session Authentication but any auth should work.
        """

        filename_req = request.data.get('filename')
        if not filename_req:
            return Response({"message": "A filename is required"}, status=status.HTTP_400_BAD_REQUEST)
        policy_expires = int(time.time() + 5000)
        """
        image_url - media/customer_slug/ortho/YYYYMMDD/uuid.<tif/png/jpg>
        """
        upload_start_path, obj_uuid, filename_final, username_str, ortho_obj = create_image_object(filename_req)
        url, policy, signature = get_policy(policy_expires, upload_start_path)

        data = {
            "policy": policy,
            "signature": signature,
            "key": settings.AWS_ACCESS_KEY_ID,
            "file_bucket_path": upload_start_path,
            "file_uuid": obj_uuid,
            "filename": filename_final,
            "url": url,
            "username": username_str,
        }

        return Response(data, status=status.HTTP_200_OK)


class MapView(LoginRequiredMixin, DetailView):

    def get_queryset(self):
        obj_id = int(self.kwargs['id'])
        q_set = OrthoImage.objects.filter(id=obj_id)
        return q_set

    def get_object(self, queryset=None):
        obj_id = int(self.kwargs['id'])
        obj = OrthoImage.objects.get(id=obj_id)
        return obj

    def get_context_data(self, **kwargs):
        obj_id = int(self.kwargs['id'])
        ortho_obj = OrthoImage.objects.get(id=obj_id)
        tile_obj = TileImage.objects.filter(parent_ortho__id=obj_id).first()
        first_tile_url = tile_obj.image_url
        first_tile_name = tile_obj.tile_name
        folder_url = None
        if first_tile_url:
            folder_url = first_tile_url.split(first_tile_name)[0]
        context_data = super(MapView, self).get_context_data(**kwargs)
        print(ortho_obj.tile_coordinates)
        context_data.update({'folder_url': folder_url, "latitude": ortho_obj.latitude, "longitude": ortho_obj.longitude,
                             "coordinates": ortho_obj.tile_coordinates})
        return context_data


class FileSuccessAPI(APIView):

    def post(self, request, *args, **kwargs):
        ortho_output = tile_creating_function(request.POST['upload_url'], request.POST['file'])
        if type(ortho_output) == int:
            success_url = reverse('map-page', kwargs={'id': ortho_output})
            data = {"result": "Success", "urls": success_url}
            return Response(data, status=status.HTTP_200_OK)
        else:
            data = {'result': ortho_output}     # Error message
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
