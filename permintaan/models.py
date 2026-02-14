from django.db import models
from django.contrib.auth.models import User

class PermintaanBarang(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Disetujui'),
        ('rejected', 'Ditolak'),
        ('delivered', 'Dikirim'),
    ]

    peminta = models.ForeignKey(User, on_delete=models.CASCADE)
    barang = models.ForeignKey('gudang.Consumable', on_delete=models.CASCADE)
    jumlah = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    tanggal = models.DateTimeField(auto_now_add=True)
    catatan = models.TextField(blank=True)

    def __str__(self):
        return f"{self.barang} - {self.status}"
