import subprocess
import os

from django.utils import timezone
from django.core.mail import send_mail

from .models import PerangkatJaringan, NetworkLog
from notifikasi.whatsapp import kirim_wa


# ======================
# PING DEVICE
# ======================

def ping_device(ip):

    # Windows pakai -n | Linux pakai -c
    param = "-n" if os.name == "nt" else "-c"

    command = ["ping", param, "1", ip]

    try:
        result = subprocess.run(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=3
        )
        return result.returncode == 0

    except subprocess.TimeoutExpired:
        return False


# ======================
# CEK STATUS + SIMPAN LOG
# ======================

def cek_status_jaringan():

    devices = PerangkatJaringan.objects.all()

    for d in devices:

        # ===== SIMPAN STATUS LAMA =====
        status_lama = d.last_status

        # ===== CEK STATUS BARU =====
        if ping_device(d.ip_address):
            status_baru = "up"
        else:
            status_baru = "down"

        # ===== UPDATE DEVICE =====
        d.last_status = status_baru
        d.last_checked = timezone.now()
        d.save()

        # ===== SIMPAN LOG =====
        NetworkLog.objects.create(
            perangkat=d,
            status=status_baru
        )

        # =================================
        # 🚨 SAAT JARINGAN DARI UP → DOWN
        # =================================
        if status_lama == "up" and status_baru == "down":

            pesan = "🚨 ALERT DOWNTIME SERVER / JARINGAN 🚨\n\n"
            pesan += f"Perangkat : {d.nama}\n"
            pesan += f"IP : {d.ip_address}\n"
            pesan += f"Waktu : {d.last_checked}\n"

            # ===== EMAIL =====
            send_mail(
                subject="ALERT JARINGAN RS",
                message=pesan,
                from_email=None,
                recipient_list=['angga.sundux@gmail.com'],
                fail_silently=False,
            )

            # ===== WHATSAPP =====
            kirim_wa(pesan)

        # =================================
        # ✅ SAAT JARINGAN DARI DOWN → UP
        # =================================
        if status_lama == "down" and status_baru == "up":

            pesan = (
                "✅ JARINGAN NORMAL KEMBALI\n\n"
                f"Perangkat : {d.nama}\n"
                f"IP : {d.ip_address}\n"
                f"Waktu : {d.last_checked}\n"
            )

            # ===== EMAIL =====
            send_mail(
                subject="JARINGAN NORMAL KEMBALI",
                message=pesan,
                from_email=None,
                recipient_list=['angga.sundux@gmail.com'],
                fail_silently=False,
            )

            # ===== WHATSAPP =====
            kirim_wa(pesan)
