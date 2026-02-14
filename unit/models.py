from django.db import models
from django.contrib.auth.models import User
from lokasi.models import Ruangan
from jaringan.models import PerangkatJaringan


class UnitKomputer(models.Model):

    STATUS = [
        ('aktif', 'Aktif'),
        ('maintenance', 'Maintenance'),
        ('rusak', 'Rusak'),
        ('nonaktif', 'Non Aktif'),
    ]

    nama_unit = models.CharField(max_length=150)
    hostname = models.CharField(max_length=150, blank=True)

    ip_address = models.GenericIPAddressField()
    mac_address = models.CharField(max_length=50, blank=True)

    ruangan = models.ForeignKey(
        Ruangan,
        on_delete=models.SET_NULL,
        null=True
    )

    pengguna = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    terhubung_ke = models.ForeignKey(
        PerangkatJaringan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    sistem_operasi = models.CharField(max_length=100, blank=True)
    spesifikasi = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default='aktif'
    )

    tanggal_input = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nama_unit} - {self.ip_address}"
