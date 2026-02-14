from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import UnitKomputer
from lokasi.models import Ruangan
from jaringan.models import PerangkatJaringan
from django.core.paginator import Paginator


# ======================
# LIST
# ======================

@login_required
def unit_list(request):

    data = UnitKomputer.objects.select_related(
        'ruangan', 'pengguna', 'terhubung_ke'
    ).order_by('-tanggal_input')

    paginator = Paginator(data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'unit/list.html', {
        'data': page_obj
    })


# ======================
# TAMBAH
# ======================

@login_required
def unit_add(request):

    ruangan_list = Ruangan.objects.all()
    user_list = User.objects.all()
    perangkat_list = PerangkatJaringan.objects.all()

    if request.method == "POST":

        UnitKomputer.objects.create(
            nama_unit=request.POST['nama_unit'],
            hostname=request.POST.get('hostname'),
            ip_address=request.POST['ip_address'],
            mac_address=request.POST.get('mac_address'),
            ruangan_id=request.POST['ruangan'],
            pengguna_id=request.POST.get('pengguna'),
            terhubung_ke_id=request.POST.get('terhubung_ke'),
            sistem_operasi=request.POST.get('sistem_operasi'),
            spesifikasi=request.POST.get('spesifikasi'),
            status=request.POST['status'],
        )

        return redirect('unit_list')

    return render(request, 'unit/form.html', {
        'ruangan_list': ruangan_list,
        'user_list': user_list,
        'perangkat_list': perangkat_list
    })


# ======================
# EDIT
# ======================

@login_required
def unit_edit(request, id):

    unit = get_object_or_404(UnitKomputer, id=id)

    ruangan_list = Ruangan.objects.all()
    user_list = User.objects.all()
    perangkat_list = PerangkatJaringan.objects.all()

    if request.method == "POST":

        unit.nama_unit = request.POST['nama_unit']
        unit.hostname = request.POST.get('hostname')
        unit.ip_address = request.POST['ip_address']
        unit.mac_address = request.POST.get('mac_address')
        unit.ruangan_id = request.POST['ruangan']
        unit.pengguna_id = request.POST.get('pengguna')
        unit.terhubung_ke_id = request.POST.get('terhubung_ke')
        unit.sistem_operasi = request.POST.get('sistem_operasi')
        unit.spesifikasi = request.POST.get('spesifikasi')
        unit.status = request.POST['status']

        unit.save()

        return redirect('unit_list')

    return render(request, 'unit/form.html', {
        'unit': unit,
        'ruangan_list': ruangan_list,
        'user_list': user_list,
        'perangkat_list': perangkat_list
    })


# ======================
# DELETE
# ======================

@login_required
def unit_delete(request, id):

    unit = get_object_or_404(UnitKomputer, id=id)
    unit.delete()

    return redirect('unit_list')


from django.http import HttpResponse
from openpyxl import Workbook
from .models import UnitKomputer

@login_required
def export_unit_excel(request):

    data = UnitKomputer.objects.select_related(
        'ruangan', 'pengguna'
    ).all()

    wb = Workbook()
    ws = wb.active
    ws.title = "Data Unit Komputer"

    # Header
    ws.append([
        "Kode Unit",
        "Nama Komputer",
        "IP Address",
        "MAC Address",
        "Ruangan",
        "Pengguna",
        "Status",
        "Keterangan"
    ])

    # Data
    for d in data:
        ws.append([
            d.kode_unit,
            d.nama_komputer,
            d.ip_address,
            d.mac_address or "-",
            d.ruangan.nama if d.ruangan else "-",
            d.pengguna.username if d.pengguna else "-",
            d.status,
            d.keterangan or "-"
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=data_unit_komputer.xlsx'

    wb.save(response)
    return response

@login_required
def unit_list(request):

    data = UnitKomputer.objects.select_related(
        'ruangan', 'pengguna', 'terhubung_ke'
    ).order_by('-tanggal_input')

    total = data.count()
    aktif = data.filter(status='aktif').count()
    maintenance = data.filter(status='maintenance').count()
    rusak = data.filter(status='rusak').count()
    nonaktif = data.filter(status='nonaktif').count()

    paginator = Paginator(data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'unit/list.html', {
        'data': page_obj,
        'total': total,
        'aktif': aktif,
        'maintenance': maintenance,
        'rusak': rusak,
        'nonaktif': nonaktif,
    })
