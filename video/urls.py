from django.urls import path
from . import views

urlpatterns = [
    path('upload', views.UploadView.as_view(template_name='create.html'), name='upload'),
    path('dashboard', views.OrthoListView.as_view(template_name='list.html'), name='list'),
    path('map/<id>/', views.MapView.as_view(template_name='map.html'), name='map-page'),
    path(r'api/files/policy/', views.FilePolicyAPI.as_view(), name='upload-policy'),
    path(r'api/upload/complete/', views.FileSuccessAPI.as_view(), name='upload-complete'),
]
