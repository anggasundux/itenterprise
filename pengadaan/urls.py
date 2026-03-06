from django.urls import path
from . import views

app_name = 'pengadaan'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    
    # SPPB
    path('sppb/', views.list_sppb, name='list_sppb'),
    path('sppb/buat/', views.create_sppb, name='create_sppb'),
    path('sppb/<int:pk>/', views.detail_sppb, name='detail_sppb'),
    path('sppb/<int:sppb_id>/barang/add/', views.add_detail_barang, name='add_detail_barang'),
    path('sppb/<int:pk>/status/', views.update_status_sppb, name='update_status'),
    
    # Laporan & Vendor
    path('laporan/', views.laporan_bulanan, name='laporan'),
    path('vendor/', views.list_vendor, name='list_vendor'),
    path('vendor/buat/', views.create_vendor, name='create_vendor'),
    path('vendor/<int:pk>/edit/', views.edit_vendor, name='edit_vendor'),
    path('vendor/<int:pk>/delete/', views.delete_vendor, name='delete_vendor'),
]