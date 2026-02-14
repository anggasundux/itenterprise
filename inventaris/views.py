from django.shortcuts import render, redirect, get_object_or_404
from django.db import IntegrityError
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.http import HttpResponse
from django.template.loader import get_template

from xhtml2pdf import pisa

from .models import Aset, MutasiAset
from lokasi.models import Ruangan


# ================= LIST =================

def inventaris_list(request):
    data = Aset.objects.select_related('ruangan').all()
    return render(request, 'inventaris/list.html', {
        'data': data
    })


# ================= TAMBAH =================

def inventaris_add(request):
    ruangan_list = Ruangan.objects.all()

    if request.method == "POST":
        try:
            Aset.objects.create(
                kode_aset=request.POST['kode_aset'],
                nama_aset=request.POST['nama_aset'],
                kategori=request.POST['kategori'],
                merek=request.POST['merek'],
                nomor_seri=request.POST['nomor_seri'],
                ruangan_id=request.POST['ruangan'],
                kondisi=request.POST['kondisi'],
                tanggal_beli=request.POST['tanggal_beli'],
                keterangan=request.POST['keterangan'],
            )
            return redirect('inventaris_list')

        except IntegrityError:
            return render(request, 'inventaris/form.html', {
                'ruangan_list': ruangan_list,
                'error': 'Kode aset sudah ada!'
            })

    return render(request, 'inventaris/form.html', {
        'ruangan_list': ruangan_list
    })


# ================= EDIT =================

def inventaris_edit(request, id):
    aset = get_object_or_404(Aset, id=id)
    ruangan_list = Ruangan.objects.all()

    if request.method == "POST":
        aset.kode_aset = request.POST['kode_aset']
        aset.nama_aset = request.POST['nama_aset']
        aset.kategori = request.POST['kategori']
        aset.merek = request.POST['merek']
        aset.nomor_seri = request.POST['nomor_seri']
        aset.ruangan_id = request.POST['ruangan']
        aset.kondisi = request.POST['kondisi']
        aset.tanggal_beli = request.POST['tanggal_beli']
        aset.keterangan = request.POST['keterangan']
        aset.save()

        return redirect('inventaris_list')

    return render(request, 'inventaris/form.html', {
        'aset': aset,
        'ruangan_list': ruangan_list
    })


# ================= HAPUS =================

def inventaris_delete(request, id):
    aset = get_object_or_404(Aset, id=id)
    aset.delete()
    return redirect('inventaris_list')


# ================= DETAIL + HISTORI =================

def aset_detail(request, kode):
    aset = get_object_or_404(Aset, kode_aset=kode)
    histori = MutasiAset.objects.filter(aset=aset).order_by('-tanggal')

    return render(request, 'inventaris/detail.html', {
        'aset': aset,
        'histori': histori
    })


# ================= MUTASI =================

def mutasi_aset(request, id):
    aset = get_object_or_404(Aset, id=id)
    ruangan_list = Ruangan.objects.all()

    if request.method == "POST":
        ruangan_baru = Ruangan.objects.get(id=request.POST['ruangan'])

        MutasiAset.objects.create(
            aset=aset,
            dari_ruangan=aset.ruangan,
            ke_ruangan=ruangan_baru
        )

        aset.ruangan = ruangan_baru
        aset.save()

        return redirect('inventaris_list')

    return render(request, 'inventaris/mutasi.html', {
        'aset': aset,
        'ruangan_list': ruangan_list
    })


# ================= CETAK BARCODE =================

def cetak_barcode(request, id):
    aset = get_object_or_404(Aset, id=id)
    return render(request, 'inventaris/cetak_barcode.html', {
        'aset': aset
    })


# ================= PDF =================

def pdf_inventaris(request):
    aset = Aset.objects.all()
    template = get_template('inventaris/pdf_inventaris.html')
    html = template.render({'aset': aset})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="inventaris.pdf"'

    pisa.CreatePDF(html, dest=response)
    return response


def pdf_mutasi(request):
    mutasi = MutasiAset.objects.all().order_by('-tanggal')

    template = get_template('inventaris/pdf_mutasi.html')
    html = template.render({'mutasi': mutasi})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="mutasi_aset.pdf"'

    pisa.CreatePDF(html, dest=response)
    return response


# ================= REKAP RUANGAN =================

def rekap_ruangan(request):
    rekap = Aset.objects.values('ruangan__nama').annotate(
        total=Count('id')
    )

    return render(request, 'inventaris/rekap_ruangan.html', {
        'rekap': rekap
    })


# ================= GRAFIK SIMPLE =================

def grafik_dashboard(request):
    per_ruangan = Aset.objects.values('ruangan__nama').annotate(total=Count('id'))
    kondisi = Aset.objects.values('kondisi').annotate(total=Count('id'))

    return render(request, 'inventaris/grafik.html', {
        'per_ruangan': per_ruangan,
        'kondisi': kondisi
    })


# ================= LIST MUTASI + FILTER TANGGAL =================

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

def total_aset_rusak(request):

    aset_rusak = Aset.objects.filter(kondisi="Rusak").count()

    return render(request, 'inventaris/aset_rusak.html', {
        'aset_rusak': aset_rusak
    })
