from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError

from laporan.utils import buat_slip_pengeluaran
from gudang.models import PengeluaranConsumable

from .models import PermintaanBarang
from .utils import notif_status


# ======================
# LIST PERMINTAAN
# ======================

@login_required
def daftar_permintaan(request):

    permintaan_list = PermintaanBarang.objects.order_by('-tanggal')

    return render(request, 'permintaan/daftar.html', {
        'permintaan_list': permintaan_list
    })


# ======================
# APPROVE PERMINTAAN
# ======================

@login_required
def approve_permintaan(request, id):

    permintaan = get_object_or_404(PermintaanBarang, id=id)

    permintaan.status = "approved"
    permintaan.save()

    notif_status(
        f"Permintaan {permintaan.barang.nama_barang} "
        f"({permintaan.jumlah}) sudah disetujui"
    )

    return redirect('daftar_permintaan')


# ======================
# KIRIM BARANG (AUTO STOK + PDF)
# ======================

@login_required
def kirim_barang(request, id):

    permintaan = get_object_or_404(PermintaanBarang, id=id)

    if permintaan.status != "approved":
        return redirect('daftar_permintaan')

    barang = permintaan.barang

    # cek stok cukup
    if barang.stok < permintaan.jumlah:
        raise ValidationError("Stok tidak mencukupi")

    # buat pengeluaran (auto potong stok)
    PengeluaranConsumable.objects.create(
        barang=barang,
        jumlah=permintaan.jumlah,
        digunakan_oleh=request.user,
        keterangan=f"Permintaan #{permintaan.id}"
    )

    # update status
    permintaan.status = "delivered"
    permintaan.save()

    # 👉 BUAT PDF SLIP OTOMATIS
    buat_slip_pengeluaran(permintaan)

    # notifikasi WA
    notif_status(
        f"Barang {barang.nama_barang} sejumlah {permintaan.jumlah} sudah dikirim"
    )

    return redirect('daftar_permintaan')
