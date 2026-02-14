
from django.db import models

class Laporan(models.Model):
    nama = models.CharField(max_length=100)
    periode = models.DateField(auto_now_add=True)
    file = models.FileField(upload_to='laporan/', null=True, blank=True)

    def __str__(self):
        return self.nama
