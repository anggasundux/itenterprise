from django.core.mail import send_mail
from django.utils import timezone
from .models import JadwalPemeliharaan

def kirim_reminder():
    hari_ini = timezone.now().date()

    jadwal = JadwalPemeliharaan.objects.filter(
        tanggal_jadwal=hari_ini,
        status='terjadwal'
    )

    for j in jadwal:
        send_mail(
            subject='Reminder Pemeliharaan Aset RS',
            message=f'Aset {j.aset.nama_aset} harus dilakukan pemeliharaan hari ini.',
            from_email=None,
            recipient_list=[j.dibuat_oleh.email],
        )
