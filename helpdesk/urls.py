from django.urls import path
from . import views

urlpatterns = [
    path('', views.tiket_list, name='tiket_list'),
    path('tambah/', views.tiket_add, name='tiket_add'),

    path('edit/<int:id>/', views.tiket_edit, name='tiket_edit'),
    path('delete/<int:id>/', views.tiket_delete, name='tiket_delete'),

    path('status/<int:id>/<str:status>/', views.tiket_update_status, name='tiket_update_status'),
    path('assign/<int:id>/', views.tiket_assign_petugas, name='tiket_assign_petugas'),
    path('detail/<int:id>/', views.tiket_detail, name='tiket_detail'),

    path('export/', views.export_tiket, name='export_tiket'),
]
