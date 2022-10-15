from django.urls import path
from . import views

urlpatterns = [
    path('upload', views.UploadView.as_view(template_name='create.html'), name='upload'),
    path('evaupload', views.EvaUploadView.as_view(template_name='evaporate.html'), name='eva-upload'),
    path('map/<id>/', views.MapView.as_view(template_name='map.html'), name='map-page'),
    path('list', views.image_list, name='image_list'),
    path(r'api/files/policy/', views.FilePolicyAPI.as_view(), name='upload-policy'),
    path(r'api/upload/complete/', views.FileSuccessAPI.as_view(), name='upload-complete'),
    path(r'api/signedurl', views.FileAuthAPI.as_view(), name='signer-url'),
    path(r'api/auth', views.EvaporateBaseExampleAPI.as_view(), name='auth-sign'),
]
