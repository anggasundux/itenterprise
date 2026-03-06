from django.db import models
from django.contrib.auth.models import User
from lokasi.models import Ruangan
from jaringan.models import PerangkatJaringan
from inventaris.models import Aset


# ==============================
# UNIT KOMPUTER
# ==============================

class UnitKomputer(models.Model):

    STATUS = [
        ('aktif', 'Aktif'),
        ('maintenance', 'Maintenance'),
        ('rusak', 'Rusak'),
        ('nonaktif', 'Non Aktif'),
    ]

    # CPU diambil dari inventaris
    aset = models.ForeignKey(
        Aset,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dipakai_sebagai_cpu'
    )

    nama_unit = models.CharField(max_length=150)
    hostname = models.CharField(max_length=150, blank=True)

    ip_address = models.GenericIPAddressField(unique=True)
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


# ==============================
# PERANGKAT TAMBAHAN
# ==============================

class PerangkatTambahan(models.Model):

    JENIS = [
        ('monitor', 'Monitor'),
        ('printer', 'Printer'),
        ('keyboard', 'Keyboard'),
        ('mouse', 'Mouse'),
        ('scanner', 'Scanner'),
        ('lainnya', 'Lainnya'),
    ]

    unit = models.ForeignKey(
        UnitKomputer,
        on_delete=models.CASCADE,
        related_name='perangkat_tambahan'
    )

    aset = models.ForeignKey(
        Aset,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dipakai_sebagai_perangkat'
    )

    jenis = models.CharField(max_length=30, choices=JENIS)

    merk = models.CharField(max_length=100, blank=True)
    nomor_seri = models.CharField(max_length=100, blank=True)
    keterangan = models.TextField(blank=True)

    tanggal_pasang = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.unit.nama_unit} - {self.get_jenis_display()}"


# ==============================
# RIWAYAT PINDAH PERANGKAT
# ==============================

class RiwayatPerangkat(models.Model):

    perangkat = models.ForeignKey(
        PerangkatTambahan,
        on_delete=models.CASCADE
    )

    dari_unit = models.ForeignKey(
        UnitKomputer,
        on_delete=models.SET_NULL,
        null=True,
        related_name='riwayat_dari'
    )

    ke_unit = models.ForeignKey(
        UnitKomputer,
        on_delete=models.SET_NULL,
        null=True,
        related_name='riwayat_ke'
    )

    tanggal = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.perangkat} pindah"
