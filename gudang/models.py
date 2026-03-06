from django.db import models
from django.contrib.auth.models import User
from lokasi.models import Ruangan


# =====================
# GUDANG
# =====================

class Gudang(models.Model):
    nama = models.CharField(max_length=100)
    lokasi = models.CharField(max_length=150)
    keterangan = models.TextField(blank=True)

    def __str__(self):
        return self.nama


# =====================
# BARANG / CONSUMABLE
# =====================

class Consumable(models.Model):
    nama_barang = models.CharField(max_length=150)
    kategori = models.CharField(max_length=100, null=True, blank=True)
    satuan = models.CharField(max_length=50, null=True, blank=True)
    stok = models.IntegerField(default=0)
    gudang = models.ForeignKey(Gudang, on_delete=models.CASCADE)
    batas_minimum = models.IntegerField(default=5)

    def __str__(self):
        return self.nama_barang


# =====================
# PENGELUARAN BARANG
# =====================

class PengeluaranConsumable(models.Model):

    barang = models.ForeignKey(
        Consumable,
        on_delete=models.CASCADE
    )

    ruangan = models.ForeignKey(
        Ruangan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    jumlah = models.IntegerField()
    tanggal = models.DateTimeField(auto_now_add=True)

    digunakan_oleh = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )

    keterangan = models.TextField(blank=True)

    def __str__(self):
        return f"{self.barang.nama_barang} - {self.jumlah}"

    # =====================
    # UPDATE STOK OTOMATIS
    # =====================

    def save(self, *args, **kwargs):

        if self.pk:
            old = PengeluaranConsumable.objects.get(pk=self.pk)
            selisih = self.jumlah - old.jumlah
        else:
            selisih = self.jumlah

        if self.barang.stok - selisih < 0:
            raise ValueError("Stok tidak mencukupi!")

        self.barang.stok -= selisih
        self.barang.save()

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):

        self.barang.stok += self.jumlah
        self.barang.save()

        super().delete(*args, **kwargs)