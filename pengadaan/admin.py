from django.contrib import admin
from .models import SPPB, DetailSPPB, LaporanBulanan

@admin.register(SPPB)
class SPPBAdmin(admin.ModelAdmin):
    list_display = ['nomor_sppb', 'ruangan', 'unit', 'status', 'tanggal_sppb', 'created_at']
    list_filter = ['status', 'tanggal_sppb', 'unit']
    search_fields = ['nomor_sppb']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(DetailSPPB)
class DetailSPPBAdmin(admin.ModelAdmin):
    list_display = ['nama_barang', 'jumlah', 'harga_satuan', 'total_harga', 'sppb']
    list_filter = ['sppb__status', 'created_at']
    search_fields = ['nama_barang']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(LaporanBulanan)
class LaporanBulananAdmin(admin.ModelAdmin):
    list_display = ['bulan', 'total_sppb', 'total_nominal', 'barang_datang', 'barang_verified', 'barang_masuk_inventaris']
    list_filter = ['bulan']
    readonly_fields = ['created_at']