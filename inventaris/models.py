from django.db import models
from lokasi.models import Ruangan
import qrcode
from io import BytesIO
from django.core.files import File

class Aset(models.Model):
    KONDISI_CHOICES = [
        ('Baik', 'Baik'),
        ('Rusak', 'Rusak'),
        ('Maintenance', 'Maintenance'),
        ('Baru', 'Baru'),
    ]
    
    kode_aset = models.CharField(max_length=50, unique=True)
    nama_aset = models.CharField(max_length=150)
    kategori = models.CharField(max_length=100)
    merek = models.CharField(max_length=100, blank=True)
    nomor_seri = models.CharField(max_length=100, blank=True)
    ruangan = models.ForeignKey(Ruangan, on_delete=models.SET_NULL, null=True)
    kondisi = models.CharField(max_length=50, choices=KONDISI_CHOICES, default='Baik')
    tanggal_beli = models.DateField()
    keterangan = models.TextField(blank=True)
    

    def __str__(self):
        return f"{self.kode_aset} - {self.nama_aset}"


    barcode = models.ImageField(upload_to='barcode/', blank=True)

    def save(self, *args, **kwargs):
        if not self.barcode:
            url = f"http://10.10.10.166:8000/inventaris/detail/{self.kode_aset}/"
            qr = qrcode.make(url)
            buffer = BytesIO()
            qr.save(buffer, format='PNG')
            self.barcode.save(f'{self.kode_aset}.png', File(buffer), save=False)

        super().save(*args, **kwargs)


from django.utils import timezone

class MutasiAset(models.Model):
    aset = models.ForeignKey(Aset, on_delete=models.CASCADE)
    dari_ruangan = models.ForeignKey(
        Ruangan, related_name='mutasi_dari',
        on_delete=models.SET_NULL, null=True
    )
    ke_ruangan = models.ForeignKey(
        Ruangan, related_name='mutasi_ke',
        on_delete=models.SET_NULL, null=True
    )
    tanggal = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.aset.kode_aset} : {self.dari_ruangan} → {self.ke_ruangan}"


