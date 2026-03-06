from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import datetime
from .models import SPPB, DetailSPPB, LaporanBulanan, Vendor
from .forms import SPPBForm, DetailSPPBForm, UpdateStatusSPPBForm, VendorForm
from inventaris.models import Aset
import json

@login_required
def dashboard(request):
    """Dashboard Pengadaan"""
    total_sppb = SPPB.objects.count()
    total_dipesan = SPPB.objects.filter(status='dipesan').count()
    total_datang = SPPB.objects.filter(status='datang').count()
    total_verified = SPPB.objects.filter(status='diverifikasi').count()
    
    recent_sppb = SPPB.objects.all()[:5]
    pending_barang = DetailSPPB.objects.filter(
        sppb__status__in=['dipesan', 'datang']
    ).select_related('sppb').order_by('-created_at')[:10]
    
    context = {
        'total_sppb': total_sppb,
        'total_dipesan': total_dipesan,
        'total_datang': total_datang,
        'total_verified': total_verified,
        'recent_sppb': recent_sppb,
        'pending_barang': pending_barang,
    }
    return render(request, 'pengadaan/dashboard.html', context)

@login_required
def list_sppb(request):
    """List SPPB"""
    sppb_list = SPPB.objects.all()
    status_filter = request.GET.get('status')
    
    if status_filter:
        sppb_list = sppb_list.filter(status=status_filter)
    
    context = {
        'sppb_list': sppb_list,
        'status_choices': SPPB.STATUS_CHOICES,
    }
    return render(request, 'pengadaan/sppb_list.html', context)

@login_required
def create_sppb(request):
    """Buat SPPB baru"""
    if request.method == 'POST':
        form = SPPBForm(request.POST, request.FILES)
        if form.is_valid():
            sppb = form.save(commit=False)
            sppb.created_by = request.user.username
            # jika unit tidak diisi, isi otomatis dari nama ruangan (server-side fallback)
            if not sppb.unit and sppb.ruangan:
                try:
                    sppb.unit = str(sppb.ruangan.nama)
                except Exception:
                    sppb.unit = ''
            sppb.save()
            return redirect('pengadaan:detail_sppb', pk=sppb.pk)
        else:
            # debug: print form errors to console to help tests
            import logging
            logger = logging.getLogger(__name__)
            logger.warning('SPPB form invalid: %s', form.errors)
            logger.warning('request.POST keys: %s', list(request.POST.keys()))
            logger.warning('request.FILES keys: %s', list(request.FILES.keys()))
    else:
        form = SPPBForm()
    
    return render(request, 'pengadaan/sppb_form.html', {
        'form': form,
        'title': 'Buat SPPB Baru'
    })

@login_required
def detail_sppb(request, pk):
    """Detail SPPB & List Barang"""
    sppb = get_object_or_404(SPPB, pk=pk)
    detail_barang = sppb.detail_barang.all()
    total_nominal = detail_barang.aggregate(Sum('harga_satuan'))['harga_satuan__sum'] or 0
    
    context = {
        'sppb': sppb,
        'detail_list': detail_barang,
        'total_nominal': total_nominal,
    }
    return render(request, 'pengadaan/sppb_detail.html', context)

@login_required
def add_detail_barang(request, sppb_id):
    """Tambah barang ke SPPB"""
    sppb = get_object_or_404(SPPB, pk=sppb_id)
    
    if request.method == 'POST':
        form = DetailSPPBForm(request.POST)
        if form.is_valid():
            detail = form.save(commit=False)
            detail.sppb = sppb
            detail.save()
            return redirect('pengadaan:detail_sppb', pk=sppb.pk)
    else:
        form = DetailSPPBForm()
    
    return render(request, 'pengadaan/detail_barang_form.html', {
        'form': form,
        'sppb': sppb,
        'title': 'Tambah Barang'
    })

@login_required
def update_status_sppb(request, pk):
    """Update status SPPB"""
    sppb = get_object_or_404(SPPB, pk=pk)
    
    if request.method == 'POST':
        form = UpdateStatusSPPBForm(request.POST, instance=sppb)
        if form.is_valid():
            sppb = form.save()
            
            # Auto create Aset jika status masuk_inventaris
            if sppb.status == 'masuk_inventaris':
                # create inventory assets for each detail record that hasn't been linked yet
                for detail in sppb.detail_barang.select_for_update():
                    if not detail.aset_inventaris:
                        # generate unique asset code, avoid collision by appending detail PK
                        kode = f"{sppb.nomor_sppb}-{detail.pk}"
                        aset = Aset.objects.create(
                            kode_aset=kode,
                            nama_aset=detail.nama_barang,
                            kategori='Pengadaan',
                            merek='',
                            nomor_seri='',
                            ruangan=sppb.ruangan,
                            kondisi='Baru',
                            tanggal_beli=sppb.tanggal_sppb or timezone.now().date(),
                            keterangan=sppb.catatan or ''
                        )
                        detail.aset_inventaris = aset
                        detail.save()
            
            return redirect('pengadaan:detail_sppb', pk=sppb.pk)
    else:
        form = UpdateStatusSPPBForm(instance=sppb)
    
    return render(request, 'pengadaan/update_status_form.html', {
        'form': form,
        'sppb': sppb,
        'title': 'Update Status SPPB'
    })

@login_required
def laporan_bulanan(request):
    """Laporan Pengadaan Bulanan"""
    year = request.GET.get('year', timezone.now().year)
    month = request.GET.get('month', timezone.now().month)
    
    start_date = datetime(int(year), int(month), 1).date()
    if int(month) == 12:
        end_date = datetime(int(year) + 1, 1, 1).date()
    else:
        end_date = datetime(int(year), int(month) + 1, 1).date()
    
    sppb_bulan = SPPB.objects.filter(created_at__date__range=[start_date, end_date])
    
    total_sppb = sppb_bulan.count()
    total_nominal = sppb_bulan.aggregate(Sum('detail_barang__harga_satuan'))['detail_barang__harga_satuan__sum'] or 0
    barang_datang = sppb_bulan.filter(status='datang').count()
    barang_verified = sppb_bulan.filter(status='diverifikasi').count()
    barang_masuk = sppb_bulan.filter(status='masuk_inventaris').count()
    
    context = {
        'bulan': start_date.strftime('%B %Y'),
        'year': year,
        'month': month,
        'sppb_list': sppb_bulan,
        'total_sppb': total_sppb,
        'total_nominal': total_nominal,
        'barang_datang': barang_datang,
        'barang_verified': barang_verified,
        'barang_masuk': barang_masuk,
    }
    return render(request, 'pengadaan/laporan_bulanan.html', context)

@login_required
def list_vendor(request):
    """List Vendor"""
    vendors = Vendor.objects.all()
    return render(request, 'pengadaan/vendor_list.html', {'vendors': vendors})

@login_required
def create_vendor(request):
    """Create or edit a vendor"""
    if request.method == 'POST':
        form = VendorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('pengadaan:list_vendor')
    else:
        form = VendorForm()
    return render(request, 'pengadaan/vendor_form.html', {
        'form': form,
        'title': 'Buat Vendor Baru'
    })


@login_required
def edit_vendor(request, pk):
    vendor = get_object_or_404(Vendor, pk=pk)
    if request.method == 'POST':
        form = VendorForm(request.POST, instance=vendor)
        if form.is_valid():
            form.save()
            return redirect('pengadaan:list_vendor')
    else:
        form = VendorForm(instance=vendor)
    return render(request, 'pengadaan/vendor_form.html', {
        'form': form,
        'title': 'Edit Vendor'
    })


@login_required
def delete_vendor(request, pk):
    vendor = get_object_or_404(Vendor, pk=pk)
    vendor.delete()
    return redirect('pengadaan:list_vendor')