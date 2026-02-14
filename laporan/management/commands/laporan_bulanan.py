from django.core.management.base import BaseCommand
from laporan.utils import buat_laporan_bulanan


class Command(BaseCommand):

    help = "Generate laporan gudang bulanan"

    def handle(self, *args, **kwargs):

        buat_laporan_bulanan()

        self.stdout.write("Laporan bulanan berhasil dibuat")
