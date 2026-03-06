from django.db import models
from django.utils import timezone
from inventaris.models import Aset
from lokasi.models import Ruangan

class Vendor(models.Model):
    nama = models.CharField(max_length=255)
    kontak = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    alamat = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nama
    
    class Meta:
        verbose_name_plural = "Vendor"

class SPPB(models.Model):
    """Surat Pembelian Barang dari Tim Pembelian"""
    STATUS_CHOICES = [
        ('dipesan', 'Dipesan'),
        ('datang', 'Datang'),
        ('diverifikasi', 'Diverifikasi'),
        ('masuk_inventaris', 'Masuk Inventaris'),
    ]
    
    nomor_sppb = models.CharField(max_length=100, unique=True)
    tanggal_sppb = models.DateField()
    # file SPPB bisa bersifat optional agar alur pengujian dan import data lebih fleksibel
    file_sppb = models.FileField(upload_to='pengadaan/sppb/', null=True, blank=True)
    
    # buat sementara nullable agar migrasi aman (ada baris lama tanpa nilai)
    ruangan = models.ForeignKey(Ruangan, on_delete=models.PROTECT, null=True, blank=True)
    # sebelumnya unit disimpan sebagai CharField di migrasi awal; gunakan CharField
    # untuk konsistensi dengan migrasi yang sudah ada
    unit = models.CharField(max_length=255)
    keterangan = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='dipesan')
    
    # Tracking
    tanggal_datang = models.DateField(null=True, blank=True)
    tanggal_verifikasi = models.DateField(null=True, blank=True)
    catatan = models.TextField(blank=True)
    
    created_by = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.nomor_sppb
    
    class Meta:
        ordering = ['-created_at']

class DetailSPPB(models.Model):
    """Detail barang dalam SPPB"""
    sppb = models.ForeignKey(SPPB, on_delete=models.CASCADE, related_name='detail_barang')
    nama_barang = models.CharField(max_length=255)
    spesifikasi = models.TextField(blank=True)
    jumlah = models.IntegerField()
    satuan = models.CharField(max_length=50, default='Unit')
    harga_satuan = models.DecimalField(max_digits=12, decimal_places=2)
    aset_inventaris = models.ForeignKey(Aset, on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.nama_barang} ({self.sppb.nomor_sppb})"
    
    @property
    def total_harga(self):
        return self.harga_satuan * self.jumlah
    
    class Meta:
        verbose_name_plural = "Detail SPPB"

class LaporanBulanan(models.Model):
    """Laporan Pengadaan Bulanan"""
    bulan = models.DateField()
    total_sppb = models.IntegerField(default=0)
    total_nominal = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    barang_datang = models.IntegerField(default=0)
    barang_verified = models.IntegerField(default=0)
    barang_masuk_inventaris = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Laporan {self.bulan.strftime('%B %Y')}"
    
    class Meta:
        ordering = ['-bulan']
        verbose_name_plural = "Laporan Bulanan"