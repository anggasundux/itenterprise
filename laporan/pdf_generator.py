from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from django.utils import timezone
from django.db.models import Count

from inventaris.models import Aset
from helpdesk.models import Tiket
from jaringan.models import NetworkLog
from gudang.utils import cek_stok_minimum


def generate_laporan_pdf(file_path):

    styles = getSampleStyleSheet()
    styles["Title"].alignment = TA_CENTER

    elements = []

    now = timezone.now()

    elements.append(Paragraph("LAPORAN IT RUMAH SAKIT", styles["Title"]))
    elements.append(Paragraph(f"Bulan: {now.strftime('%B %Y')}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    # =====================
    # DATA RINGKAS
    # =====================

    total_aset = Aset.objects.count()
    total_tiket = Tiket.objects.count()
    tiket_selesai = Tiket.objects.filter(status="selesai").count()

    elements.append(Paragraph(f"Total Aset: {total_aset}", styles["Normal"]))
    elements.append(Paragraph(f"Total Tiket: {total_tiket}", styles["Normal"]))
    elements.append(Paragraph(f"Tiket Selesai: {tiket_selesai}", styles["Normal"]))

    elements.append(Spacer(1, 12))

    # =====================
    # DOWNTIME
    # =====================

    start_month = now.replace(day=1)

    downtime = NetworkLog.objects.filter(
        status="down",
        waktu__gte=start_month
    ).count()

    elements.append(Paragraph(f"Downtime Bulan Ini: {downtime} kali", styles["Normal"]))

    # =====================
    # STOK MINIM
    # =====================

    stok_minim = cek_stok_minimum()

    elements.append(Spacer(1, 12))
    elements.append(Paragraph("Stok Minim:", styles["Normal"]))

    if stok_minim.exists():
        table_data = [["Barang", "Sisa"]]

        for b in stok_minim:
            table_data.append([b.nama_barang, b.stok])

        table = Table(table_data)
        table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ]))

        elements.append(table)
    else:
        elements.append(Paragraph("Semua stok aman", styles["Normal"]))

    # =====================
    # SAVE PDF
    # =====================

    doc = SimpleDocTemplate(file_path, pagesize=A4)
    doc.build(elements)
