from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.paginator import Paginator
from django.http import HttpResponse

from openpyxl import Workbook

from .models import Tiket, HistoriTiket
from lokasi.models import Ruangan
from notifikasi.whatsapp import kirim_wa


# ======================
# LIST TIKET
# ======================

@login_required
def tiket_list(request):

    start = request.GET.get('start')
    end = request.GET.get('end')
    status = request.GET.get('status')

    data = Tiket.objects.select_related(
        'ruangan','pelapor','petugas'
    ).order_by('-tanggal_buat')

    if start and end and start != "None" and end != "None":
        data = data.filter(tanggal_buat__date__range=[start, end])

    if status and status != "None":
        data = data.filter(status=status)

    paginator = Paginator(data, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'helpdesk/list.html', {
        'data': page_obj,
        'start': start,
        'end': end,
        'status': status
    })


# ======================
# EXPORT EXCEL
# ======================

@login_required
def export_tiket(request):

    start = request.GET.get('start')
    end = request.GET.get('end')
    status = request.GET.get('status')

    data = Tiket.objects.select_related('ruangan','pelapor','petugas')

    if start and end and start != "None" and end != "None":
        data = data.filter(tanggal_buat__date__range=[start, end])

    if status and status != "None":
        data = data.filter(status=status)

    wb = Workbook()
    ws = wb.active
    ws.title = "Laporan Helpdesk"

    ws.append([
        "No Tiket","Judul","Ruangan","Prioritas",
        "Status","Pelapor","Petugas","Tanggal"
    ])

    for t in data:
        ws.append([
            t.nomor_tiket,
            t.judul,
            t.ruangan.nama if t.ruangan else "-",
            t.prioritas.upper(),
            t.status.upper(),
            t.pelapor.username,
            t.petugas.username if t.petugas else "-",
            timezone.localtime(t.tanggal_buat).strftime("%d-%m-%Y %H:%M")
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=laporan_helpdesk.xlsx'
    wb.save(response)

    return response


# ======================
# TAMBAH TIKET
# ======================

@login_required
def tiket_add(request):

    ruangan_list = Ruangan.objects.all()

    if request.method == "POST":

        tiket = Tiket.objects.create(
            judul=request.POST['judul'],
            keluhan=request.POST['keluhan'],
            ruangan_id=request.POST['ruangan'],
            prioritas=request.POST['prioritas'],
            pelapor=request.user
        )

        pesan = f"""
📢 Tiket Baru Masuk

No Tiket : {tiket.nomor_tiket}
Judul : {tiket.judul}
Ruangan : {tiket.ruangan}
Prioritas : {tiket.prioritas.upper()}
Status : {tiket.status.upper()}
Pelapor : {tiket.pelapor.username}
"""

        kirim_wa(pesan)

        return redirect('tiket_list')

    return render(request, 'helpdesk/form.html', {
        'ruangan_list': ruangan_list
    })


# ======================
# UPDATE STATUS (WIB)
# ======================

@login_required
def tiket_update_status(request, id, status):

    tiket = get_object_or_404(Tiket, id=id)
    tiket.status = status

    # jika selesai → simpan waktu WIB
    if status == 'selesai':
        tiket.tanggal_selesai = timezone.localtime(timezone.now())

    tiket.save()

    HistoriTiket.objects.create(
        tiket=tiket,
        status=status
    )

    # format WIB
    waktu_selesai = (
        timezone.localtime(tiket.tanggal_selesai).strftime("%d-%m-%Y %H:%M WIB")
        if tiket.tanggal_selesai else "-"
    )

    nama_petugas = tiket.petugas.username if tiket.petugas else "Belum ditugaskan"

    if status == 'selesai':

        pesan = f"""
✅ Tiket Selesai

No Tiket : {tiket.nomor_tiket}
Judul : {tiket.judul}
Ruangan : {tiket.ruangan}

Petugas : {nama_petugas}
Waktu Selesai : {waktu_selesai}
"""

    else:

        pesan = f"""
📌 Update Status Tiket

No Tiket : {tiket.nomor_tiket}
Judul : {tiket.judul}
Status Baru : {status.upper()}
"""

    kirim_wa(pesan)

    return redirect('tiket_list')


# ======================
# ASSIGN PETUGAS
# ======================

@login_required
def tiket_assign_petugas(request, id):

    tiket = get_object_or_404(Tiket, id=id)
    petugas_list = User.objects.all()

    if request.method == "POST":

        tiket.petugas_id = request.POST['petugas']

        # otomatis jadi proses
        tiket.status = 'proses'
        tiket.save()

        HistoriTiket.objects.create(
            tiket=tiket,
            status='proses'
        )

        pesan = f"""
👨‍🔧 Petugas Ditugaskan

No Tiket : {tiket.nomor_tiket}
Judul : {tiket.judul}
Petugas : {tiket.petugas.username}
Status : PROSES
"""

        kirim_wa(pesan)

        return redirect('tiket_list')

    return render(request, 'helpdesk/assign.html', {
        'tiket': tiket,
        'petugas_list': petugas_list
    })


# ======================
# DETAIL
# ======================

@login_required
def tiket_detail(request, id):

    tiket = get_object_or_404(Tiket, id=id)

    histori = HistoriTiket.objects.filter(
        tiket=tiket
    ).order_by('-waktu')

    return render(request, 'helpdesk/detail.html', {
        'tiket': tiket,
        'histori': histori
    })


# ======================
# EDIT
# ======================

@login_required
def tiket_edit(request, id):

    tiket = get_object_or_404(Tiket, id=id)
    ruangan_list = Ruangan.objects.all()

    if request.method == "POST":

        tiket.judul = request.POST['judul']
        tiket.keluhan = request.POST['keluhan']
        tiket.ruangan_id = request.POST['ruangan']
        tiket.prioritas = request.POST['prioritas']

        tiket.save()

        return redirect('tiket_list')

    return render(request, 'helpdesk/form.html', {
        'ruangan_list': ruangan_list,
        'tiket': tiket
    })


# ======================
# DELETE
# ======================

@login_required
def tiket_delete(request, id):

    tiket = get_object_or_404(Tiket, id=id)

    HistoriTiket.objects.filter(tiket=tiket).delete()

    pesan = f"""
🗑 Tiket Dihapus

No Tiket : {tiket.nomor_tiket}
Judul : {tiket.judul}
"""

    kirim_wa(pesan)

    tiket.delete()

    return redirect('tiket_list')
