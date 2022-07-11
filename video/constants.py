from django.conf import settings


POLICY_DOCUMENT_CONTEXT = {
        "expire": "",
        "bucket_name": settings.AWS_STORAGE_BUCKET_NAME,
        "key_name": "",
        "acl_name": "public-read",
        "content_name": "",
        "content_length": 524288000,
        "upload_start_path": '',

    }
