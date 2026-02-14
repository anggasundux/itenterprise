from django.shortcuts import render
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.contrib.auth.decorators import login_required
import json

from inventaris.models import Aset
from helpdesk.models import Tiket
from pemeliharaan.models import JadwalPemeliharaan
from gudang.models import PengeluaranConsumable
from gudang.utils import cek_stok_minimum
from jaringan.models import PerangkatJaringan, NetworkLog


# ======================
# DASHBOARD HOME (WAJIB LOGIN)
# ======================

@login_required(login_url='/login/')
def dashboard_home(request):

    # ===== RINGKASAN =====

    total_aset = Aset.objects.count()
    aset_rusak = Aset.objects.filter(kondisi="Rusak").count()

    total_tiket = Tiket.objects.count()
    tiket_aktif = Tiket.objects.exclude(status='selesai').count()

    tiket_baru = Tiket.objects.filter(status='baru').count()
    tiket_proses = Tiket.objects.filter(status='proses').count()
    tiket_selesai = Tiket.objects.filter(status='selesai').count()
    tiket_ditutup = Tiket.objects.filter(status='ditutup').count()

    maintenance_hari_ini = JadwalPemeliharaan.objects.filter(
        tanggal_jadwal=timezone.now().date()
    ).count()

    stok_minim = cek_stok_minimum().count()
    alert_stok = cek_stok_minimum()

    perangkat_jaringan = PerangkatJaringan.objects.all()

    # ======================
    # GRAFIK TIKET PER BULAN
    # ======================

    tiket_per_bulan = (
        Tiket.objects
        .annotate(bulan=TruncMonth('tanggal_buat'))
        .values('bulan')
        .annotate(total=Count('id'))
        .order_by('bulan')
    )

    bulan_labels = []
    bulan_data = []

    for t in tiket_per_bulan:
        if t['bulan']:
            bulan_labels.append(t['bulan'].strftime('%b %Y'))
            bulan_data.append(t['total'])

    # ======================
    # GRAFIK CONSUMABLE
    # ======================

    consumable_per_bulan = (
        PengeluaranConsumable.objects
        .annotate(bulan=TruncMonth('tanggal'))
        .values('bulan')
        .annotate(total=Sum('jumlah'))
        .order_by('bulan')
    )

    cons_labels = []
    cons_data = []

    for c in consumable_per_bulan:
        if c['bulan']:
            cons_labels.append(c['bulan'].strftime('%b %Y'))
            cons_data.append(c['total'] or 0)

    # ======================
    # GRAFIK DOWNTIME
    # ======================

    downtime = (
        NetworkLog.objects
        .filter(status="down")
        .annotate(bulan=TruncMonth('waktu'))
        .values('bulan')
        .annotate(total=Count('id'))
        .order_by('bulan')
    )

    down_labels = []
    down_data = []

    for d in downtime:
        if d['bulan']:
            down_labels.append(d['bulan'].strftime('%b %Y'))
            down_data.append(d['total'])

    # ======================
    # HITUNG UPTIME
    # ======================

    start_month = timezone.now().replace(day=1)

    total_log = NetworkLog.objects.filter(
        waktu__gte=start_month
    ).count()

    down_log = NetworkLog.objects.filter(
        waktu__gte=start_month,
        status="down"
    ).count()

    if total_log > 0:
        uptime_percent = round(
            ((total_log - down_log) / total_log) * 100, 2
        )
    else:
        uptime_percent = 100

    # ======================
    # KIRIM KE TEMPLATE
    # ======================

    return render(request, 'dashboard/home.html', {

        # aset
        'total_aset': total_aset,
        'aset_rusak': aset_rusak,

        # tiket
        'total_tiket': total_tiket,
        'tiket_aktif': tiket_aktif,
        'tiket_baru': tiket_baru,
        'tiket_proses': tiket_proses,
        'tiket_selesai': tiket_selesai,
        'tiket_ditutup': tiket_ditutup,

        # maintenance & stok
        'maintenance_hari_ini': maintenance_hari_ini,
        'stok_minim': stok_minim,
        'alert_stok': alert_stok,

        # jaringan
        'perangkat_jaringan': perangkat_jaringan,

        # grafik
        'bulan_labels': json.dumps(bulan_labels),
        'bulan_data': json.dumps(bulan_data),

        'cons_labels': json.dumps(cons_labels),
        'cons_data': json.dumps(cons_data),

        'down_labels': json.dumps(down_labels),
        'down_data': json.dumps(down_data),

        # uptime
        'uptime_percent': uptime_percent,
    })


# ======================
# REALTIME JARINGAN (WAJIB LOGIN)
# ======================

@login_required(login_url='/login/')
def realtime_status(request):

    devices = PerangkatJaringan.objects.all()
    data = []

    for d in devices:
        data.append({
            'nama': d.nama,
            'ip': d.ip_address,
            'status': d.last_status,
            'last_checked': d.last_checked.strftime("%H:%M:%S") if d.last_checked else "-"
        })

    return JsonResponse({'devices': data})
