import uuid
from django.db import models
from django.contrib.auth.models import User


class Upload(models.Model):
    image = models.ImageField(upload_to='media/')
    name = models.CharField(max_length=256)


class BaseAbstractModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class Customer(BaseAbstractModel):
    customer_name = models.CharField(max_length=2048)
    customer_slug = models.CharField(max_length=2048, null=True, blank=True)

    def __str__(self):
        return str(self.id) + '-' + str(self.customer_name)

    def save(self, *args, **kwargs):
        if self.customer_slug == '' or self.customer_slug is None:
            self.customer_slug = str(self.customer_name).lower().replace(' ', '_')
        super(Customer, self).save(*args, **kwargs)


class OrthoImage(BaseAbstractModel):
    IMAGE_TYPES = ((0, 'rgb'), (1, 'multi-spectral'), (2, 'hyper-spectral'))
    ortho_name = models.CharField(max_length=2048)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    tile_coordinates = models.CharField(max_length=2048, null=True, blank=True)
    image_url = models.URLField(null=True, blank=True)
    image_type = models.CharField(max_length=256, choices=IMAGE_TYPES, null=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        return str(self.id) + '-' + str(self.ortho_name) + '-' + str(self.uuid)


class TileImage(BaseAbstractModel):
    IMAGE_TYPES = ((0, 'rgb'), (1, 'multi-spectral'), (2, 'hyper-spectral'))
    tile_name = models.CharField(max_length=2048)
    image_url = models.URLField(null=True, blank=True)
    image_type = models.CharField(max_length=256, choices=IMAGE_TYPES, null=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    parent_ortho = models.ForeignKey(OrthoImage, on_delete=models.CASCADE, null=True, blank=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        return str(self.id) + '-' + str(self.tile_name) + '-' + str(self.uuid)


class CustomUser(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user_obj = models.ForeignKey(User, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id) + '-' + str(self.customer.customer_name) + '-' + str(self.user_obj.username)


# ToDo Remove null True Blank True in required fields after loop is completed
