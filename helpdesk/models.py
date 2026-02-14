from django.db import models, transaction
from django.utils import timezone
from django.contrib.auth.models import User
from lokasi.models import Ruangan


class Tiket(models.Model):

    PRIORITAS = [
        ('rendah', 'Rendah'),
        ('sedang', 'Sedang'),
        ('tinggi', 'Tinggi'),
        ('kritis', 'Kritis'),
    ]

    STATUS = [
        ('baru', 'Baru'),
        ('proses', 'Proses'),
        ('selesai', 'Selesai'),
        ('ditutup', 'Ditutup'),
    ]

    judul = models.CharField(max_length=200)
    keluhan = models.TextField()

    ruangan = models.ForeignKey(
        Ruangan,
        on_delete=models.SET_NULL,
        null=True
    )

    prioritas = models.CharField(max_length=20, choices=PRIORITAS)
    status = models.CharField(max_length=20, choices=STATUS, default='baru')

    pelapor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='pelapor'
    )

    petugas = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='petugas'
    )

    tanggal_buat = models.DateTimeField(auto_now_add=True)
    tanggal_selesai = models.DateTimeField(null=True, blank=True)

    nomor_tiket = models.CharField(
        max_length=30,
        unique=True,
        blank=True
    )

    def save(self, *args, **kwargs):

        if not self.nomor_tiket:
            tanggal = timezone.now().strftime("%Y%m%d")

            with transaction.atomic():

                terakhir = (
                    Tiket.objects
                    .filter(nomor_tiket__startswith=f"TKT-{tanggal}")
                    .count()
                )

                urut = terakhir + 1
                self.nomor_tiket = f"TKT-{tanggal}-{urut:03d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return self.nomor_tiket


class HistoriTiket(models.Model):

    tiket = models.ForeignKey(
        Tiket,
        on_delete=models.CASCADE
    )

    status = models.CharField(max_length=20)

    waktu = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tiket.nomor_tiket} - {self.status}"
