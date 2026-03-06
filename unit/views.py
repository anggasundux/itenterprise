from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.db import models
from openpyxl import Workbook

from .models import UnitKomputer, PerangkatTambahan
from lokasi.models import Ruangan
from jaringan.models import PerangkatJaringan
from inventaris.models import Aset


# =====================================================
# LIST
# =====================================================

@login_required
def unit_list(request):
    # basic queryset with related fields for performance
    qs = UnitKomputer.objects.select_related(
        'ruangan', 'pengguna', 'terhubung_ke', 'aset'
    ).prefetch_related('perangkat_tambahan').order_by('-tanggal_input')

    # search / filter parameters
    q = request.GET.get('q', '').strip()
    status = request.GET.get('status', '')

    if q:
        # search by name or ip address
        qs = qs.filter(
            models.Q(nama_unit__icontains=q) | models.Q(ip_address__icontains=q)
        )

    if status in ['aktif', 'maintenance', 'rusak', 'nonaktif']:
        qs = qs.filter(status=status)

    total = UnitKomputer.objects.count()
    aktif = UnitKomputer.objects.filter(status='aktif').count()
    maintenance = UnitKomputer.objects.filter(status='maintenance').count()
    rusak = UnitKomputer.objects.filter(status='rusak').count()
    nonaktif = UnitKomputer.objects.filter(status='nonaktif').count()

    paginator = Paginator(qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'unit/list.html', {
        'data': page_obj,
        'total': total,
        'aktif': aktif,
        'maintenance': maintenance,
        'rusak': rusak,
        'nonaktif': nonaktif,
        'search_query': q,
        'filter_status': status,
    })


# =====================================================
# ADD UNIT
# =====================================================

@login_required
def unit_add(request):

    ruangan_list = Ruangan.objects.all()
    user_list = User.objects.all()
    perangkat_list = PerangkatJaringan.objects.all()

    # tampilkan semua aset (nanti bisa difilter kategori CPU)
    aset_list = Aset.objects.all()

    if request.method == "POST":

        ip = request.POST['ip_address']

        if UnitKomputer.objects.filter(ip_address=ip).exists():
            return render(request, 'unit/form.html', {
                'error': 'IP Address sudah digunakan!',
                'ruangan_list': ruangan_list,
                'user_list': user_list,
                'perangkat_list': perangkat_list,
                'aset_list': aset_list
            })

        UnitKomputer.objects.create(
            aset_id=request.POST.get('aset') or None,
            nama_unit=request.POST['nama_unit'],
            hostname=request.POST.get('hostname') or "",
            ip_address=ip,
            mac_address=request.POST.get('mac_address') or "",
            ruangan_id=request.POST.get('ruangan') or None,
            pengguna_id=request.POST.get('pengguna') or None,
            terhubung_ke_id=request.POST.get('terhubung_ke') or None,
            sistem_operasi=request.POST.get('sistem_operasi') or "",
            spesifikasi=request.POST.get('spesifikasi') or "",
            status=request.POST['status'],
        )

        return redirect('unit_list')

    return render(request, 'unit/form.html', {
        'ruangan_list': ruangan_list,
        'user_list': user_list,
        'perangkat_list': perangkat_list,
        'aset_list': aset_list
    })


# =====================================================
# EDIT
# =====================================================

@login_required
def unit_edit(request, id):

    unit = get_object_or_404(UnitKomputer, id=id)

    ruangan_list = Ruangan.objects.all()
    user_list = User.objects.all()
    perangkat_list = PerangkatJaringan.objects.all()
    aset_list = Aset.objects.all()

    if request.method == "POST":

        ip = request.POST['ip_address']

        if UnitKomputer.objects.exclude(id=id).filter(ip_address=ip).exists():
            return render(request, 'unit/form.html', {
                'unit': unit,
                'error': 'IP Address sudah digunakan!',
                'ruangan_list': ruangan_list,
                'user_list': user_list,
                'perangkat_list': perangkat_list,
                'aset_list': aset_list
            })

        unit.aset_id = request.POST.get('aset') or None
        unit.nama_unit = request.POST['nama_unit']
        unit.hostname = request.POST.get('hostname') or ""
        unit.ip_address = ip
        unit.mac_address = request.POST.get('mac_address') or ""
        unit.ruangan_id = request.POST.get('ruangan') or None
        unit.pengguna_id = request.POST.get('pengguna') or None
        unit.terhubung_ke_id = request.POST.get('terhubung_ke') or None
        unit.sistem_operasi = request.POST.get('sistem_operasi') or ""
        unit.spesifikasi = request.POST.get('spesifikasi') or ""
        unit.status = request.POST['status']

        unit.save()

        return redirect('unit_list')

    return render(request, 'unit/form.html', {
        'unit': unit,
        'ruangan_list': ruangan_list,
        'user_list': user_list,
        'perangkat_list': perangkat_list,
        'aset_list': aset_list
    })


# =====================================================
# DELETE  ⭐ INI YANG ERROR TADI
# =====================================================

@login_required
def unit_delete(request, id):
    unit = get_object_or_404(UnitKomputer, id=id)
    unit.delete()
    return redirect('unit_list')


# =====================================================
# DETAIL
# =====================================================

@login_required
def unit_detail(request, id):

    unit = get_object_or_404(
        UnitKomputer.objects.select_related(
            'ruangan', 'pengguna', 'terhubung_ke', 'aset'
        ).prefetch_related('perangkat_tambahan'),
        id=id
    )

    return render(request, 'unit/detail.html', {
        'unit': unit
    })


# =====================================================
# TAMBAH PERANGKAT
# =====================================================

@login_required
def perangkat_add(request, unit_id):

    unit = get_object_or_404(UnitKomputer, id=unit_id)
    aset_list = Aset.objects.all()

    if request.method == "POST":
        PerangkatTambahan.objects.create(
            unit=unit,
            jenis=request.POST['jenis'],
            aset_id=request.POST.get('aset') or None,
            merk=request.POST.get('merk'),
            nomor_seri=request.POST.get('nomor_seri'),
            keterangan=request.POST.get('keterangan'),
        )
        return redirect('unit_detail', id=unit.id)

    return render(request, 'unit/perangkat_form.html', {
        'unit': unit,
        'aset_list': aset_list
    })


# =====================================================
# DELETE PERANGKAT
# =====================================================

@login_required
def perangkat_delete(request, id):
    p = get_object_or_404(PerangkatTambahan, id=id)
    unit_id = p.unit.id
    p.delete()
    return redirect('unit_detail', id=unit_id)


# =====================================================
# EXPORT
# =====================================================

@login_required
def export_unit_excel(request):

    data = UnitKomputer.objects.prefetch_related(
        'perangkat_tambahan'
    ).select_related('ruangan', 'pengguna', 'aset')

    wb = Workbook()
    ws = wb.active
    ws.title = "Unit"

    ws.append([
        "Nama Unit",
        "CPU",
        "IP",
        "Ruangan",
        "Status",
        "Perangkat"
    ])

    for unit in data:

        perangkat = unit.perangkat_tambahan.all()

        if perangkat.exists():
            for p in perangkat:
                ws.append([
                    unit.nama_unit,
                    unit.aset.nama_aset if unit.aset else "-",
                    unit.ip_address,
                    unit.ruangan.nama if unit.ruangan else "-",
                    unit.status,
                    p.get_jenis_display(),
                ])
        else:
            ws.append([
                unit.nama_unit,
                unit.aset.nama_aset if unit.aset else "-",
                unit.ip_address,
                unit.ruangan.nama if unit.ruangan else "-",
                unit.status,
                "-"
            ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=unit.xlsx'

    wb.save(response)
    return response
