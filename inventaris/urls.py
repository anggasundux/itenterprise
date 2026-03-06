from django.urls import path
from . import views

urlpatterns = [

    path('', views.inventaris_list, name='inventaris_list'),
    path('add/', views.inventaris_add, name='inventaris_add'),
    path('edit/<int:id>/', views.inventaris_edit, name='inventaris_edit'),
    path('delete/<int:id>/', views.inventaris_delete, name='inventaris_delete'),
    path('detail/<str:kode>/', views.aset_detail, name='aset_detail'),
    path('mutasi/<int:id>/', views.mutasi_aset, name='mutasi_aset'),
    path('cetak-barcode/<int:id>/', views.cetak_barcode, name='cetak_barcode'),
    path('pdf-inventaris/', views.pdf_inventaris, name='pdf_inventaris'),
    path('pdf-mutasi/', views.pdf_mutasi, name='pdf_mutasi'),
    path('rekap-ruangan/', views.rekap_ruangan, name='rekap_ruangan'),
    path('grafik/', views.grafik_dashboard, name='grafik_dashboard'),
    path('mutasi-list/', views.mutasi_list, name='mutasi_list'),
    path('rekap-mutasi-bulanan/', views.rekap_mutasi_bulanan, name='rekap_mutasi_bulanan'),
    path('aset-rusak/', views.total_aset_rusak, name='aset_rusak'),

]
