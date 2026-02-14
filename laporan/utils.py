from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
import os
from django.conf import settings


def buat_slip_pengeluaran(permintaan):

    file_path = os.path.join(
        settings.MEDIA_ROOT,
        f"slip_pengeluaran_{permintaan.id}.pdf"
    )

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(file_path, pagesize=A4)

    content = [
        Paragraph("RUMAH SAKIT - SLIP PENGELUARAN BARANG IT", styles['Title']),
        Spacer(1, 12),
        Paragraph(f"Tanggal: {permintaan.tanggal}", styles['Normal']),
        Paragraph(f"Barang: {permintaan.barang.nama_barang}", styles['Normal']),
        Paragraph(f"Jumlah: {permintaan.jumlah}", styles['Normal']),
        Paragraph(f"Peminta: {permintaan.peminta.username}", styles['Normal']),
        Spacer(1, 20),
        Paragraph("Dikeluarkan oleh Gudang IT", styles['Normal']),
    ]

    doc.build(content)

    return file_path


from django.db.models import Sum
from gudang.models import PengeluaranConsumable
from django.utils import timezone


def get_laporan_bulanan():

    bulan_ini = timezone.now().month
    tahun_ini = timezone.now().year

    data = (
        PengeluaranConsumable.objects
        .filter(
            tanggal__month=bulan_ini,
            tanggal__year=tahun_ini
        )
        .values('barang__nama_barang')
        .annotate(total=Sum('jumlah'))
        .order_by('-total')
    )

    return data

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
import os
from django.conf import settings


def buat_laporan_bulanan():

    file_path = os.path.join(
        settings.MEDIA_ROOT,
        "laporan_gudang_bulanan.pdf"
    )

    data = get_laporan_bulanan()

    rows = [["Barang", "Total Pemakaian"]]

    for d in data:
        rows.append([d['barang__nama_barang'], d['total']])

    doc = SimpleDocTemplate(file_path)

    table = Table(rows)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ]))

    content = [
        Paragraph("LAPORAN GUDANG IT BULANAN", getSampleStyleSheet()['Title']),
        Spacer(1, 12),
        table
    ]

    doc.build(content)

    return file_path
