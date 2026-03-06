from inventaris.models import Aset

def pembelian_terima(request, id):
    p = get_object_or_404(PengajuanPembelian, id=id)

    # buat aset
    for i in range(p.jumlah):
        Aset.objects.create(
            kode_aset=f"AUTO-{p.id}-{i}",
            nama_aset=p.nama_barang,
            kategori=p.kategori,
            kondisi="baru",
            tanggal_beli=date.today(),
        )

    p.status = "diterima"
    p.save()

    return redirect("pembelian_list")
