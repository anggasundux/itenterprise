from django.db import models
from django.core.mail import send_mail
from .models import Consumable


def cek_stok_minimum():
    return Consumable.objects.filter(
        stok__lte=models.F('batas_minimum')
    )


def kirim_alert_stok():

    barang_minim = cek_stok_minimum()

    if not barang_minim.exists():
        return

    pesan = "Stok consumable hampir habis:\n\n"

    for b in barang_minim:
        pesan += f"{b.nama_barang} - sisa {b.stok}\n"

    send_mail(
        subject="ALERT STOK IT RS",
        message=pesan,
        from_email=None,
        recipient_list=['angga.sundux@gmail.com'],  # ganti emailmu
        fail_silently=False,
    )
