from django.contrib import admin
from .models import Upload, Customer, OrthoImage, TileImage, CustomUser

# Register your models here.
admin.site.register(Upload)
admin.site.register(Customer)
admin.site.register(OrthoImage)
admin.site.register(TileImage)
admin.site.register(CustomUser)
