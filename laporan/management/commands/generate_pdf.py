from django.core.management.base import BaseCommand
from laporan.pdf_generator import generate_laporan_pdf
from django.utils import timezone
from django.core.mail import EmailMessage
from notifikasi.whatsapp import kirim_wa
import os


class Command(BaseCommand):
    help = "Generate & kirim PDF laporan IT bulanan"

    def handle(self, *args, **kwargs):

        now = timezone.now()

        filename = f"laporan_IT_{now.strftime('%Y_%m')}.pdf"
        file_path = os.path.join(os.getcwd(), filename)

        # =====================
        # GENERATE PDF
        # =====================

        generate_laporan_pdf(file_path)

        # =====================
        # KIRIM EMAIL
        # =====================

        email = EmailMessage(
            subject=f"Laporan IT Bulan {now.strftime('%B %Y')}",
            body="Terlampir laporan IT rumah sakit.",
            to=["angga.sundux@gmail.com"]  # bisa tambah email lain
        )

        email.attach_file(file_path)
        email.send()

        # =====================
        # KIRIM WHATSAPP
        # =====================

        pesan_wa = f"📄 Laporan IT Bulan {now.strftime('%B %Y')} sudah dibuat dan dikirim ke email."

        kirim_wa("6285647212000", pesan_wa)   # nomor kamu

        self.stdout.write(self.style.SUCCESS("PDF dibuat & dikirim sukses"))
