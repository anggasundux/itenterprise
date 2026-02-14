from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import F, Sum

from .models import Consumable, PengeluaranConsumable, Gudang
from lokasi.models import Ruangan


# ======================
# LIST GUDANG + STOK MINIM
# ======================

def gudang_list(request):

    data = Consumable.objects.select_related('gudang')

    stok_minim = Consumable.objects.filter(
        stok__lte=F('batas_minimum')
    )

    return render(request, 'gudang/list.html', {
        'data': data,
        'stok_minim': stok_minim
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
# PENGELUARAN BARANG + RUANGAN
# ======================

@login_required
def pengeluaran_add(request):

    barang_list = Consumable.objects.all()
    ruangan_list = Ruangan.objects.all()   # 👉 ambil ruangan

    if request.method == "POST":

        PengeluaranConsumable.objects.create(
            barang_id=int(request.POST['barang']),
            ruangan_id=int(request.POST['ruangan']),   # ✅ RUANGAN TUJUAN
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
