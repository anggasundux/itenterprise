from datetime import timedelta
from django.utils import timezone
from .models import Tiket
from notifikasi.whatsapp import kirim_wa


def reminder_tiket_harian():

    batas = timezone.now() - timedelta(days=1)

    tiket_telat = Tiket.objects.filter(
        status__in=['baru', 'proses'],
        tanggal_buat__lte=batas
    )

    for t in tiket_telat:

        pesan = f"""
⏰ REMINDER TIKET HELPDESK

Judul : {t.judul}
Ruangan : {t.ruangan}
Status : {t.status.upper()}
Sejak : {t.tanggal_buat.strftime('%d-%m-%Y %H:%M')}

Mohon segera ditindaklanjuti 🙏
"""

        kirim_wa(pesan)
