from django.urls import path
from .views import *

urlpatterns = [

    # Gudang
    path('', gudang_list, name='gudang_list'),

    # CRUD barang
    path('add/', consumable_add, name='consumable_add'),
    path('edit/<int:id>/', consumable_edit, name='consumable_edit'),
    path('delete/<int:id>/', consumable_delete, name='consumable_delete'),
    path('rekap/', rekap_pengeluaran, name='rekap_pengeluaran'),

    # Pengeluaran
    path('pengeluaran/', pengeluaran_add, name='pengeluaran_add'),

    # Riwayat pengeluaran
    path('riwayat/', pengeluaran_list, name='pengeluaran_list'),

]
