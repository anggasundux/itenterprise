from django.db import models

class Gedung(models.Model):
    nama = models.CharField(max_length=100)

    def __str__(self):
        return self.nama


class Ruangan(models.Model):
    gedung = models.ForeignKey(Gedung, on_delete=models.CASCADE)
    nama = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.gedung.nama} - {self.nama}"


class Unit(models.Model):
    nama = models.CharField(max_length=100)

    def __str__(self):
        return self.nama
