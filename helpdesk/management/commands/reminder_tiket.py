from django.core.management.base import BaseCommand
from helpdesk.tasks import reminder_tiket_harian

class Command(BaseCommand):
    help = "Kirim reminder tiket harian"

    def handle(self, *args, **kwargs):
        reminder_tiket_harian()
        self.stdout.write("Reminder tiket terkirim")
