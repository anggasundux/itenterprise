from django.contrib import admin
from .models import Aset, MutasiAset


@admin.register(Aset)
class AsetAdmin(admin.ModelAdmin):
    list_display = ['kode_aset', 'nama_aset', 'kategori', 'ruangan', 'kondisi', 'tanggal_beli']
    list_filter = ['kondisi', 'kategori', 'ruangan', 'tanggal_beli']
    search_fields = ['kode_aset', 'nama_aset', 'nomor_seri']
    fieldsets = (
        ('Informasi Aset', {
            'fields': ('kode_aset', 'nama_aset', 'kategori', 'merek', 'nomor_seri')
        }),
        ('Lokasi & Kondisi', {
            'fields': ('ruangan', 'kondisi')
        }),
        ('Tanggal', {
            'fields': ('tanggal_beli',)
        }),
        ('Keterangan', {
            'fields': ('keterangan',)
        }),
    )


@admin.register(MutasiAset)
class MutasiAsetAdmin(admin.ModelAdmin):
    list_display = ['aset', 'dari_ruangan', 'ke_ruangan', 'tanggal']
    list_filter = ['tanggal', 'dari_ruangan', 'ke_ruangan']
    search_fields = ['aset__kode_aset', 'aset__nama_aset']
    readonly_fields = ['tanggal']
    date_hierarchy = 'tanggal'
