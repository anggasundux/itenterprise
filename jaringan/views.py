from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import PerangkatJaringan
from lokasi.models import Gedung, Ruangan

# ======================
# LIST
# ======================

@login_required
def jaringan_list(request):

    data = PerangkatJaringan.objects.select_related(
        'gedung','ruangan'
    ).all()

    return render(request, 'jaringan/list.html', {
        'data': data
    })


# ======================
# TAMBAH
# ======================

@login_required
def jaringan_add(request):

    gedung_list = Gedung.objects.all()
    ruangan_list = Ruangan.objects.all()

    # 👉 ambil choices jenis dari model
    jenis_list = PerangkatJaringan.JENIS

    if request.method == "POST":

        PerangkatJaringan.objects.create(
            nama=request.POST['nama'],
            jenis=request.POST['jenis'],
            ip_address=request.POST['ip_address'],
            mac_address=request.POST.get('mac_address'),
            gedung_id=request.POST['gedung'],
            ruangan_id=request.POST['ruangan'],
            status=request.POST['status'],
            keterangan=request.POST.get('keterangan','')
        )

        return redirect('jaringan_list')

    return render(request, 'jaringan/form.html', {
        'gedung_list': gedung_list,
        'ruangan_list': ruangan_list,
        'jenis_list': jenis_list
    })


# ======================
# EDIT
# ======================

@login_required
def jaringan_edit(request, id):

    perangkat = get_object_or_404(PerangkatJaringan, id=id)

    gedung_list = Gedung.objects.all()
    ruangan_list = Ruangan.objects.all()

    # 👉 ambil choices jenis juga
    jenis_list = PerangkatJaringan.JENIS

    if request.method == "POST":

        perangkat.nama = request.POST['nama']
        perangkat.jenis = request.POST['jenis']
        perangkat.ip_address = request.POST['ip_address']
        perangkat.mac_address = request.POST.get('mac_address')
        perangkat.gedung_id = request.POST['gedung']
        perangkat.ruangan_id = request.POST['ruangan']
        perangkat.status = request.POST['status']
        perangkat.keterangan = request.POST.get('keterangan','')

        perangkat.save()

        return redirect('jaringan_list')

    return render(request, 'jaringan/form.html', {
        'perangkat': perangkat,
        'gedung_list': gedung_list,
        'ruangan_list': ruangan_list,
        'jenis_list': jenis_list
    })


# ======================
# DELETE
# ======================

@login_required
def jaringan_delete(request, id):

    perangkat = get_object_or_404(PerangkatJaringan, id=id)
    perangkat.delete()

    return redirect('jaringan_list')
