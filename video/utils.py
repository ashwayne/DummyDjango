import base64
import boto3
import hashlib
import hmac
import os

from copy import deepcopy
from django.conf import settings
from django.contrib.auth.models import User
from .models import OrthoImage, Customer, TileImage, CustomUser
from .constants import POLICY_DOCUMENT_CONTEXT
from .generate_tiles import tile_gen


def create_image_object(filename_req, user_id, tile_image=False, ortho_id=None):
    # TODO: Remove temporary user, customer after creating permissions
    user = User.objects.get(id=user_id)
    username_str = str(user.username)
    custom_user = CustomUser.objects.get(user_obj=user)
    customer_obj = custom_user.customer
    if tile_image:
        filename_req = filename_req.split(str(os.path.join(settings.BASE_DIR, 'TileImages', f'{ortho_id}')) + '/')[1]
        parent_ortho_obj = OrthoImage.objects.get(id=ortho_id)
        file_obj = TileImage.objects.create(tile_name=filename_req, created_by=user, customer=customer_obj,
                                            parent_ortho=parent_ortho_obj)
    else:
        file_obj = OrthoImage.objects.create(ortho_name=filename_req, created_by=user, customer=customer_obj)
    obj_uuid = file_obj.uuid
    customer = file_obj.customer.customer_slug
    date = file_obj.created_at.strftime("%Y%m%d")
    _, file_extension = os.path.splitext(filename_req)
    if tile_image:
        upload_start_path = f"media/{customer}/tile/{date}/{ortho_id}"
        filename_final = filename_req
    else:
        upload_start_path = "media/{customer_slug}/ortho/{date}/".format(customer_slug=customer, date=date)
        filename_final = "{obj_uuid}{file_extension}".format(
            obj_uuid=obj_uuid,
            file_extension=file_extension
        )
    """
    Eventual file_upload_path includes the renamed file to the 
    Django-stored FileItem instance ID. Renaming the file is 
    done to prevent issues with user generated formatted names.
    """
    final_upload_path = "{upload_start_path}{filename_final}".format(
        upload_start_path=upload_start_path,
        filename_final=filename_final,
    )
    if filename_req and file_extension:
        file_obj.path = final_upload_path
        file_obj.save()

    return upload_start_path, obj_uuid, filename_final, username_str, file_obj


def get_policy(policy_expires, upload_start_path):
    policy_document_context = deepcopy(POLICY_DOCUMENT_CONTEXT)
    policy_document_context.update(expire=policy_expires, upload_start_path=upload_start_path)
    policy_document = """
            {"expiration": "2023-01-01T00:00:00Z",
              "conditions": [
                {"bucket": "%(bucket_name)s"},
                ["starts-with", "$key", "%(upload_start_path)s"],
                {"acl": "%(acl_name)s"},

                ["starts-with", "$Content-Type", "%(content_name)s"],
                ["starts-with", "$filename", ""],
                ["content-length-range", 0, %(content_length)d]
              ]
            }
            """ % policy_document_context
    aws_secret = str.encode(settings.AWS_SECRET_ACCESS_KEY)
    policy_document_str_encoded = str.encode(policy_document.replace(" ", ""))
    url = 'https://{custom_url}'.format(
        custom_url=settings.AWS_S3_CUSTOM_DOMAIN
    )
    policy = base64.b64encode(policy_document_str_encoded)
    signature = base64.b64encode(hmac.new(aws_secret, policy, hashlib.sha1).digest())

    return url, policy, signature


def tile_creating_function(file_url, file_uuid):
    ortho_obj = OrthoImage.objects.get(uuid=file_uuid)
    ortho_obj.image_url = file_url
    ortho_obj.save()

    images_path = os.path.join(settings.BASE_DIR, f'TileImages')
    tiles_status = tile_gen(images_path, ortho_obj.id)
    print("Tile status check: ", tiles_status)
    if type(tiles_status) == int and tiles_status == ortho_obj.id:
        images_path = os.path.join(settings.BASE_DIR, f'TileImages/{ortho_obj.id}')
        files = [os.path.join(images_path, f) for f in os.listdir(images_path) if
                 os.path.isfile(os.path.join(images_path, f))]
        session = boto3.Session(aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
        s3client = session.resource('s3')
        bucket = s3client.Bucket(settings.AWS_STORAGE_BUCKET_NAME)

        client_users = CustomUser.objects.filter(customer=ortho_obj.customer)
        if client_users:
            user_id = client_users.first().user_obj.id
        else:
            user_id = 1
        for file in files:
            upload_start_path, obj_uuid, filename_final, username_str, tile_obj = create_image_object(file, user_id,
                                                                                                      tile_image=True,
                                                                                                      ortho_id=ortho_obj.id)
            bucket.upload_file(file, '{path}/{name}'.format(path=upload_start_path, name=filename_final),
                               ExtraArgs={'ACL': 'public-read'})
            tile_url = 'https://{custom_url}/{path}/{name}'.format(custom_url=settings.AWS_S3_CUSTOM_DOMAIN,
                                                                   path=upload_start_path, name=filename_final)
            tile_obj.image_url = tile_url
            tile_obj.save()

        return ortho_obj.id
    elif type(tiles_status) == str:
        return tiles_status
