from django.urls import path
from . import views

urlpatterns = [

    path('', views.jaringan_list, name='jaringan_list'),
    path('tambah/', views.jaringan_add, name='jaringan_add'),
    path('edit/<int:id>/', views.jaringan_edit, name='jaringan_edit'),
    path('hapus/<int:id>/', views.jaringan_delete, name='jaringan_delete'),

]
