import time
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from django.conf import settings
from django.shortcuts import reverse
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Upload, OrthoImage, TileImage, CustomUser
from .utils import create_image_object, tile_creating_function, get_policy


class UploadView(LoginRequiredMixin, CreateView):
    """
    Create/Upload page base view, share data for template through context data if needed.
    """
    model = OrthoImage
    fields = ['ortho_name']


class OrthoListView(LoginRequiredMixin, ListView):
    """
    Dashboard page showing list of all the map pages with the given name
    """

    def get_queryset(self):
        user_id = self.request.user.id
        customer_obj = CustomUser.objects.get(user_obj__id=user_id).customer
        queryset = OrthoImage.objects.filter(customer=customer_obj).order_by('-created_at')
        return queryset

    def get_context_data(self, **kwargs):
        context_data = super(OrthoListView, self).get_context_data(**kwargs)
        q_set = self.get_queryset()
        thumbnails = []
        for o in q_set:
            tile = TileImage.objects.filter(parent_ortho=o, tile_name__startswith=17)
            if tile:
                thumbnails.append(tile[0].image_url)
            elif not tile and (str(o.image_url).endswith('tiff') or str(o.image_url).endswith('tif')):
                thumbnails.append(settings.DEFAULT_LAND_IMAGE)
            else:
                thumbnails.append(o.image_url)
        context_data.update({'two_lists': zip(q_set, thumbnails)})
        print(context_data['two_lists'])
        return context_data


class FilePolicyAPI(APIView):

    def post(self, request, *args, **kwargs):
        """
        API for getting pre-signed url and create an object for the ortho image to link it with DB for future reference.
        """

        # import ipdb; ipdb.set_trace()

        filename_req = request.data.get('filename')
        if not filename_req:
            return Response({"message": "A filename is required"}, status=status.HTTP_400_BAD_REQUEST)
        policy_expires = int(time.time() + 5000)
        """
        image_url - media/customer_slug/ortho/YYYYMMDD/uuid.<tif/png/jpg>
        """
        upload_start_path, obj_uuid, filename_final, username_str, ortho_obj = create_image_object(filename_req,
                                                                                                   request.user.id)
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
    """
    The map page layout view
    """

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
