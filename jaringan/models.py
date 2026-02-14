from django.db import models
from lokasi.models import Gedung, Ruangan

class PerangkatJaringan(models.Model):

    JENIS = [
        ('router', 'Router'),
        ('switch', 'Switch'),
        ('access_point', 'Access Point'),
        ('server', 'Server'),
        ('firewall', 'Firewall'),
    ]

    nama = models.CharField(max_length=150)
    jenis = models.CharField(max_length=30, choices=JENIS)

    ip_address = models.GenericIPAddressField()
    mac_address = models.CharField(max_length=50, blank=True)

    gedung = models.ForeignKey(Gedung, on_delete=models.SET_NULL, null=True)
    ruangan = models.ForeignKey(Ruangan, on_delete=models.SET_NULL, null=True)

    status = models.CharField(max_length=30)  # aktif, mati, maintenance
    keterangan = models.TextField(blank=True)
    last_status = models.CharField(max_length=20, default='unknown')
    last_checked = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.nama} ({self.ip_address})"


class VLAN(models.Model):
    nama = models.CharField(max_length=100)
    vlan_id = models.IntegerField()
    subnet = models.CharField(max_length=50)
    keterangan = models.TextField(blank=True)

    def __str__(self):
        return f"{self.nama} - {self.vlan_id}"


class PortSwitch(models.Model):
    perangkat = models.ForeignKey(PerangkatJaringan, on_delete=models.CASCADE)
    nomor_port = models.CharField(max_length=20)
    mode = models.CharField(max_length=20)  # access / trunk
    vlan = models.ForeignKey(VLAN, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.perangkat.nama} - Port {self.nomor_port}"
    

from django.db import models

class NetworkLog(models.Model):
    perangkat = models.ForeignKey(
        'PerangkatJaringan',
        on_delete=models.CASCADE
    )
    status = models.CharField(max_length=10)  # up / down
    waktu = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.perangkat.nama} - {self.status}"
