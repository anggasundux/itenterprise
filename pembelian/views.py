from inventaris.models import Aset

def pembelian_mark_datang(request, id):
    p = get_object_or_404(PengajuanPembelian, id=id)

    p.status = 'datang'
    p.save()

    # AUTO BUAT INVENTARIS
    for i in range(p.qty):
        Aset.objects.create(
            kode_aset=f"AUTO-{p.nomor}-{i+1}",
            nama_aset=p.nama_barang,
            kategori="IT",
            ruangan=p.ruangan,
            kondisi="baru",
            tanggal_beli=p.tanggal
        )

    return redirect('pembelian_list')
