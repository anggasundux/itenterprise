from django.urls import path
from .views import *

urlpatterns = [

    # ======================
    # GUDANG
    # ======================

    path('', gudang_list, name='gudang_list'),

    # ======================
    # CRUD BARANG
    # ======================

    path('add/', consumable_add, name='consumable_add'),
    path('edit/<int:id>/', consumable_edit, name='consumable_edit'),
    path('delete/<int:id>/', consumable_delete, name='consumable_delete'),

    # ======================
    # PENGELUARAN BARANG
    # ======================

    path('pengeluaran/', pengeluaran_add, name='pengeluaran_add'),

    # ======================
    # RIWAYAT PENGELUARAN
    # ======================

    path('riwayat/', pengeluaran_list, name='pengeluaran_list'),

    # ======================
    # REKAP PEMAKAIAN
    # ======================

    path('rekap/', rekap_pengeluaran, name='rekap_pengeluaran'),

    # ======================
    # LAPORAN PDF
    # ======================

    path('laporan-stok-pdf/', laporan_stok_pdf, name='laporan_stok_pdf'),

]