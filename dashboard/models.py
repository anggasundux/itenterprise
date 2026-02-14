from django.db import models

class DashboardAccess(models.Model):
    nama = models.CharField(max_length=50)

    def __str__(self):
        return self.nama
