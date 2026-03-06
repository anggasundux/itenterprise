from django.shortcuts import render, redirect, get_object_or_404
from django.db import IntegrityError
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth
from django.http import HttpResponse
from django.template.loader import get_template
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings

from xhtml2pdf import pisa

from .models import Aset, MutasiAset
from .forms import AsetForm, MutasiForm
from lokasi.models import Ruangan


# ================= LIST =================

@login_required
def inventaris_list(request):
    data = Aset.objects.select_related('ruangan').all()
    
    # Search by kode or nama
    search = request.GET.get('search', '')
    if search:
        data = data.filter(Q(kode_aset__icontains=search) | Q(nama_aset__icontains=search))
    
    # Filter by ruangan
    ruangan_filter = request.GET.get('ruangan', '')
    if ruangan_filter:
        data = data.filter(ruangan__id=ruangan_filter)
    
    # Filter by kondisi
    kondisi_filter = request.GET.get('kondisi', '')
    if kondisi_filter:
        data = data.filter(kondisi=kondisi_filter)
    
    ruangan_list = Ruangan.objects.all()
    
    return render(request, 'inventaris/list.html', {
        'data': data,
        'ruangan_list': ruangan_list,
        'search': search,
        'ruangan_filter': ruangan_filter,
        'kondisi_filter': kondisi_filter,
    })


# ================= TAMBAH =================

@login_required
def inventaris_add(request):
    if request.method == "POST":
        form = AsetForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, f'Aset {form.cleaned_data["kode_aset"]} berhasil ditambahkan!')
                return redirect('inventaris_list')
            except IntegrityError:
                messages.error(request, 'Kode aset sudah ada!')
        else:
            messages.error(request, 'Form tidak valid!')
    else:
        form = AsetForm()

    return render(request, 'inventaris/form.html', {
        'form': form,
        'title': 'Tambah Aset Baru'
    })


# ================= EDIT =================

@login_required
def inventaris_edit(request, id):
    aset = get_object_or_404(Aset, id=id)

    if request.method == "POST":
        form = AsetForm(request.POST, instance=aset)
        if form.is_valid():
            form.save()
            messages.success(request, f'Aset {aset.kode_aset} berhasil diperbarui!')
            return redirect('inventaris_list')
        else:
            messages.error(request, 'Form tidak valid!')
    else:
        form = AsetForm(instance=aset)

    return render(request, 'inventaris/form.html', {
        'form': form,
        'title': f'Edit Aset {aset.kode_aset}',
        'aset': aset
    })


# ================= HAPUS =================

@login_required
def inventaris_delete(request, id):
    aset = get_object_or_404(Aset, id=id)
    kode = aset.kode_aset
    aset.delete()
    messages.success(request, f'Aset {kode} berhasil dihapus!')
    return redirect('inventaris_list')


# ================= DETAIL + HISTORI =================

@login_required
def aset_detail(request, kode):
    aset = get_object_or_404(Aset, kode_aset=kode)
    histori = MutasiAset.objects.filter(aset=aset).order_by('-tanggal')

    return render(request, 'inventaris/detail.html', {
        'aset': aset,
        'histori': histori
    })


# ================= MUTASI =================

@login_required
def mutasi_aset(request, id):
    aset = get_object_or_404(Aset, id=id)

    if request.method == "POST":
        form = MutasiForm(request.POST)
        if form.is_valid():
            ruangan_baru = form.cleaned_data['ke_ruangan']
            
            MutasiAset.objects.create(
                aset=aset,
                dari_ruangan=aset.ruangan,
                ke_ruangan=ruangan_baru
            )

            aset.ruangan = ruangan_baru
            aset.save()

            messages.success(request, f'Aset {aset.kode_aset} berhasil dipindahkan!')
            return redirect('inventaris_list')
        else:
            messages.error(request, 'Form tidak valid!')
    else:
        form = MutasiForm()

    return render(request, 'inventaris/mutasi.html', {
        'aset': aset,
        'form': form,
        'title': f'Mutasi Aset {aset.kode_aset}'
    })


# ================= CETAK BARCODE =================

@login_required
def cetak_barcode(request, id):
    aset = get_object_or_404(Aset, id=id)
    return render(request, 'inventaris/cetak_barcode.html', {
        'aset': aset
    })


# ================= PDF =================

@login_required
def pdf_inventaris(request):
    aset = Aset.objects.all()
    template = get_template('inventaris/pdf_inventaris.html')
    html = template.render({'aset': aset})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="inventaris.pdf"'

    pisa.CreatePDF(html, dest=response)
    return response


@login_required
def pdf_mutasi(request):
    mutasi = MutasiAset.objects.all().order_by('-tanggal')

    template = get_template('inventaris/pdf_mutasi.html')
    html = template.render({'mutasi': mutasi})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="mutasi_aset.pdf"'

    pisa.CreatePDF(html, dest=response)
    return response


# ================= REKAP RUANGAN =================

@login_required
def rekap_ruangan(request):
    rekap = Aset.objects.values('ruangan__nama').annotate(
        total=Count('id')
    )

    return render(request, 'inventaris/rekap_ruangan.html', {
        'rekap': rekap
    })


# ================= GRAFIK SIMPLE =================

@login_required
def grafik_dashboard(request):
    per_ruangan = Aset.objects.values('ruangan__nama').annotate(total=Count('id'))
    kondisi = Aset.objects.values('kondisi').annotate(total=Count('id'))

    return render(request, 'inventaris/grafik.html', {
        'per_ruangan': per_ruangan,
        'kondisi': kondisi
    })


# ================= LIST MUTASI + FILTER TANGGAL =================

@login_required
def mutasi_list(request):

    start = request.GET.get('start')
    end = request.GET.get('end')

    data = MutasiAset.objects.all()

    if start and end:
        data = data.filter(tanggal__date__range=[start, end])

    return render(request, 'inventaris/mutasi_list.html', {
        'data': data
    })


# ================= REKAP MUTASI BULANAN =================

@login_required
def rekap_mutasi_bulanan(request):

    mutasi_bulanan = (
        MutasiAset.objects
        .annotate(bulan=TruncMonth('tanggal'))
        .values('bulan')
        .annotate(total=Count('id'))
        .order_by('bulan')
    )


    return render(request, 'inventaris/rekap_mutasi_bulanan.html', {
        'mutasi_bulanan': mutasi_bulanan
    })


# ================= TOTAL ASET RUSAK =================

@login_required
def total_aset_rusak(request):
    aset_rusak_list = Aset.objects.filter(kondisi="Rusak")
    aset_rusak = aset_rusak_list.count()

    return render(request, 'inventaris/aset_rusak.html', {
        'aset_rusak': aset_rusak,
        'aset_rusak_list': aset_rusak_list,
    })
