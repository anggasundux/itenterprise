from django.core.management.base import BaseCommand
from jaringan.utils import cek_status_jaringan
from gudang.utils import kirim_alert_stok


class Command(BaseCommand):
    help = "Cek jaringan + kirim notifikasi otomatis"

    def handle(self, *args, **kwargs):

        # Monitoring jaringan + alert otomatis (email + WA)
        cek_status_jaringan()

        # Alert stok gudang (jika ada)
        kirim_alert_stok()

        self.stdout.write(
            self.style.SUCCESS("Monitoring jaringan & notifikasi berhasil dijalankan")
        )
