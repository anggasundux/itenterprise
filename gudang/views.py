from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import F, Sum, Q
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

from .models import Consumable, PengeluaranConsumable, Gudang
from lokasi.models import Ruangan


# ======================
# LIST GUDANG + SEARCH + FILTER STATUS + PAGING
# ======================

def gudang_list(request):

    search = request.GET.get('search')
    status = request.GET.get('status')

    data = Consumable.objects.select_related('gudang')

    # ======================
    # SEARCH
    # ======================
    if search:
        data = data.filter(
            Q(nama_barang__icontains=search) |
            Q(kategori__icontains=search) |
            Q(gudang__nama__icontains=search)
        )

    # ======================
    # FILTER STATUS
    # ======================
    if status == "minim":
        data = data.filter(stok__lte=F('batas_minimum'))

    elif status == "aman":
        data = data.filter(stok__gt=F('batas_minimum'))

    # ======================
    # PAGINATION 15 DATA
    # ======================
    paginator = Paginator(data.order_by('nama_barang'), 15)
    page_number = request.GET.get('page')
    data = paginator.get_page(page_number)

    # ======================
    # STOK MINIMUM
    # ======================
    stok_minim = Consumable.objects.filter(
        stok__lte=F('batas_minimum')
    )

    return render(request, 'gudang/list.html', {
        'data': data,
        'stok_minim': stok_minim,
        'search': search,
        'status': status
    })


# ======================
# TAMBAH BARANG
# ======================

@login_required
def consumable_add(request):

    gudang_list = Gudang.objects.all()

    if request.method == "POST":

        Consumable.objects.create(
            nama_barang=request.POST['nama_barang'],
            kategori=request.POST['kategori'],
            stok=int(request.POST['stok']),
            satuan=request.POST['satuan'],
            gudang_id=int(request.POST['gudang']),
            batas_minimum=int(request.POST['batas_minimum'])
        )

        return redirect('gudang_list')

    return render(request, 'gudang/form.html', {
        'gudang_list': gudang_list
    })


# ======================
# EDIT BARANG
# ======================

@login_required
def consumable_edit(request, id):

    barang = get_object_or_404(Consumable, id=id)
    gudang_list = Gudang.objects.all()

    if request.method == "POST":

        barang.nama_barang = request.POST['nama_barang']
        barang.kategori = request.POST['kategori']
        barang.stok = int(request.POST['stok'])
        barang.satuan = request.POST['satuan']
        barang.gudang_id = int(request.POST['gudang'])
        barang.batas_minimum = int(request.POST['batas_minimum'])

        barang.save()

        return redirect('gudang_list')

    return render(request, 'gudang/form.html', {
        'barang': barang,
        'gudang_list': gudang_list
    })


# ======================
# HAPUS BARANG
# ======================

@login_required
def consumable_delete(request, id):

    barang = get_object_or_404(Consumable, id=id)
    barang.delete()

    return redirect('gudang_list')


# ======================
# PENGELUARAN BARANG
# ======================

@login_required
def pengeluaran_add(request):

    barang_list = Consumable.objects.all()
    ruangan_list = Ruangan.objects.all()

    if request.method == "POST":

        PengeluaranConsumable.objects.create(
            barang_id=int(request.POST['barang']),
            ruangan_id=int(request.POST['ruangan']),
            jumlah=int(request.POST['jumlah']),
            digunakan_oleh=request.user,
            keterangan=request.POST.get('keterangan', '')
        )

        return redirect('gudang_list')

    return render(request, 'gudang/pengeluaran_form.html', {
        'barang_list': barang_list,
        'ruangan_list': ruangan_list
    })


# ======================
# RIWAYAT PENGELUARAN
# ======================

def pengeluaran_list(request):

    data = PengeluaranConsumable.objects.select_related(
        'barang',
        'ruangan',
        'digunakan_oleh'
    ).order_by('-tanggal')

    return render(request, 'gudang/pengeluaran_list.html', {
        'data': data
    })


# ======================
# REKAP TOTAL PER BARANG
# ======================

def rekap_pengeluaran(request):

    data = (
        PengeluaranConsumable.objects
        .values(
            'barang__nama_barang',
            'barang__satuan'
        )
        .annotate(total_pakai=Sum('jumlah'))
        .order_by('-total_pakai')
    )

    return render(request, 'gudang/rekap_pengeluaran.html', {
        'data': data
    })


# ======================
# EXPORT PDF STOK
# ======================

def laporan_stok_pdf(request):

    data = Consumable.objects.select_related('gudang').order_by('nama_barang')

    template = get_template("gudang/laporan_stok_pdf.html")

    html = template.render({
        "data": data
    })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="laporan_stok_gudang.pdf"'

    pisa_status = pisa.CreatePDF(
        html,
        dest=response
    )

    if pisa_status.err:
        return HttpResponse('Error membuat PDF')

    return response