from django.urls import path
from . import views

urlpatterns = [
    path('', views.daftar_permintaan, name='daftar_permintaan'),
    path('approve/<int:id>/', views.approve_permintaan, name='approve_permintaan'),
    path('kirim/<int:id>/', views.kirim_barang, name='kirim_barang'),
]
