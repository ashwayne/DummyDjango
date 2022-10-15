import ast
import boto3
import time
import datetime
import hmac, hashlib, base64

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
        context_data.update({"public_key": settings.AWS_ACCESS_KEY_ID, "bucket_name": settings.AWS_STORAGE_BUCKET_NAME,
                             "signer_url": reverse('signer-url')})
        return context_data


class EvaUploadView(LoginRequiredMixin, CreateView):
    model = Upload
    fields = ['name', 'image']

    def get_context_data(self, **kwargs):
        context_data = super(EvaUploadView, self).get_context_data(**kwargs)
        context_data.update({"public_key": settings.AWS_ACCESS_KEY_ID, "bucket_name": settings.AWS_STORAGE_BUCKET_NAME,
                             "signer_url": reverse('auth-sign')})
        return context_data


def image_list(request):
    images = Upload.objects.all()
    return render(request, 'list.html', {'images': images})


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
        # import ipdb;ipdb.set_trace()
        ortho_id = tile_creating_function(request.POST['upload_url'], request.POST['file'])
        if ortho_id:
            success_url = reverse('map-page', kwargs={'id': ortho_id})
            data = {"result": "Success", "urls": success_url}
            return Response(data, status=status.HTTP_200_OK)
        else:
            data = {'result': 'Failure'}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)


class FileAuthAPI(APIView):

    def get(self, request, *args, **kwargs):
        """
        AWS V4 signature sent to front end in default
        format used by Evaporate JS
        """
        # import ipdb;ipdb.set_trace()
        print("To Sign", str(request.GET.get('to_sign').replace("\n", "").replace(' ', '')).encode('utf-8'))
        to_sign = str(request.GET.get('to_sign').replace("\n", "").replace(' ', '')).encode('utf-8')

        aws_secret = settings.AWS_SECRET_ACCESS_KEY
        date_stamp = datetime.datetime.strptime(self.request.GET.get('datetime'), '%Y%m%dT%H%M%SZ').strftime('%Y%m%d')
        region = "us-west-2"
        service = 's3'

        def sign(key, msg):
            return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

        def get_signature_key(key, date_stamp, regionName, serviceName):
            k_date = sign(str('AWS4' + key).encode('utf-8'), date_stamp)
            k_region = sign(k_date, regionName)
            k_service = sign(k_region, serviceName)
            k_signing = sign(k_service, 'aws4_request')
            return k_signing

        signing_key = get_signature_key(aws_secret, date_stamp, region, service)

        # Sign to_sign using the signing_key
        signature = hmac.new(
            signing_key,
            to_sign,
            hashlib.sha256
        ).hexdigest()

        print("*" * 50)
        print(signature)
        print("*" * 50)

        return Response(signature, status=status.HTTP_200_OK, content_type="text/HTML")


class EvaporateBaseExampleAPI(APIView):

    def get(self, request, *args, **kwargs):

        to_sign = str(request.GET.get('to_sign')).encode('utf-8')

        aws_secret = 'Dhqy88bO/9FrR0TeYDEwa5uRyA69ExHm68tok4YE'
        date_stamp = datetime.datetime.strptime(request.GET.get('datetime'), '%Y%m%dT%H%M%SZ').strftime('%Y%m%d')
        region = 'us-west-2'
        service = 's3'

        # Key derivation functions. See:
        # http://docs.aws.amazon.com/general/latest/gr/signature-v4-examples.html#signature-v4-examples-python
        def sign(key, msg):
            return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

        def getSignatureKey(key, date_stamp, regionName, serviceName):
            kDate = sign(('AWS4' + key).encode('utf-8'), date_stamp)
            kRegion = sign(kDate, regionName)
            kService = sign(kRegion, serviceName)
            kSigning = sign(kService, 'aws4_request')
            return kSigning

        signing_key = getSignatureKey(aws_secret, date_stamp, region, service)

        # Sign to_sign using the signing_key
        signature = hmac.new(
            signing_key,
            to_sign,
            hashlib.sha256
        ).hexdigest()

        return Response(signature, status=status.HTTP_200_OK, content_type="text/HTML")


# class EvaporatePolicyAPI(APIView):
#
#     def post(self, request, *args, **kwargs):
#         """
#         Evaporate API separate view
#         """
#
#         s3_client = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
#                                  aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY, region_name='us-west-2')
#         try:
#             response = s3_client.generate_presigned_post(settings.AWS_STORAGE_BUCKET_NAME,
#                                                          'media/test_cat_obj_name.jpg',
#                                                          ExpiresIn=3600)
#             response['fields']["bucket"] = settings.AWS_STORAGE_BUCKET_NAME
#             response['fields']["file_uuid"] = "SAMPLE_UUID"
#             response['fields']["filename"] = 'test_cat_obj_name.jpg'
#             response['fields']["file_bucket_path"] = 'media/'
#             response['fields']["key"] = settings.AWS_ACCESS_KEY_ID
#         except Exception as e:
#             print("Exception while creating pre-signed url: ", e)
#             return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)
#
#         return Response(response, status=status.HTTP_200_OK)
