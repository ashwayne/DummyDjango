
AWS_ACCESS_KEY_ID = 'AKIAXLODUS23BG5PCJVO'

AWS_SECRET_ACCESS_KEY = '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'

AWS_STORAGE_BUCKET_NAME = 'demdembucket'

AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'

AWS_DEFAULT_ACL = 'public-read'

AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}

# AWS_LOCATION = 'static'

AWS_QUERYSTRING_AUTH = False

AWS_HEADERS = {'Access-Control-Allow-Origin': '*'}

DEFAULT_FILE_STORAGE = 'DummyDjango.storages.MediaStorage'

STATICFILES_STORAGE = 'DummyDjango.storages.StaticStorage'

STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'

MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
