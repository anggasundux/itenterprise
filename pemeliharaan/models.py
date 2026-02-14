from django.db import models
from inventaris.models import Aset
from django.contrib.auth.models import User

class JadwalPemeliharaan(models.Model):

    JENIS = [
        ('rutin', 'Rutin'),
        ('insidental', 'Insidental'),
    ]

    aset = models.ForeignKey(Aset, on_delete=models.CASCADE)
    jenis = models.CharField(max_length=20, choices=JENIS)

    tanggal_jadwal = models.DateField()
    keterangan = models.TextField(blank=True)

    dibuat_oleh = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    status = models.CharField(max_length=30, default='terjadwal')  
    # terjadwal, selesai, tertunda

    def __str__(self):
        return f"{self.aset.nama_aset} - {self.tanggal_jadwal}"

class RiwayatPerbaikan(models.Model):
    aset = models.ForeignKey(Aset, on_delete=models.CASCADE)

    tanggal = models.DateTimeField(auto_now_add=True)
    masalah = models.TextField()
    tindakan = models.TextField()

    teknisi = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    biaya = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.aset.nama_aset} - {self.tanggal}"
