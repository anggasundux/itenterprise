from django.core.management.base import BaseCommand
from pemeliharaan.utils import kirim_reminder

class Command(BaseCommand):
    help = "Kirim reminder pemeliharaan aset"

    def handle(self, *args, **kwargs):
        kirim_reminder()
        self.stdout.write(self.style.SUCCESS("Reminder berhasil dijalankan"))
