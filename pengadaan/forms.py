from django import forms
from .models import SPPB, DetailSPPB, Vendor
from lokasi.models import Ruangan, Unit
from django.utils.safestring import mark_safe

class SPPBForm(forms.ModelForm):
    class Meta:
        model = SPPB
        fields = ['nomor_sppb', 'tanggal_sppb', 'ruangan', 'unit', 'file_sppb', 'keterangan']
        widgets = {
            'nomor_sppb': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contoh: SPPB-2026-001'
            }),
            'tanggal_sppb': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'ruangan': forms.Select(attrs={
                'class': 'form-control'
            }),
            'unit': forms.Select(attrs={
                'class': 'form-control'
            }),
            'file_sppb': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx'
            }),
            'keterangan': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Keterangan tambahan'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # populate unit dropdown from Unit model; do not enforce choice validation
        if 'unit' in self.fields:
            # if ruangan specified in form data or initial, restrict unit dropdown to that ruangan's name
            ruangan_val = None
            # check POST data first
            data = None
            if len(args) >= 1 and isinstance(args[0], dict):
                data = args[0]
            if data and data.get('ruangan'):
                ruangan_val = data.get('ruangan')
            elif 'initial' in kwargs and kwargs.get('initial') and kwargs.get('initial').get('ruangan'):
                ruangan_val = kwargs.get('initial').get('ruangan')
            elif self.instance and getattr(self.instance, 'ruangan', None):
                ruangan_val = getattr(self.instance.ruangan, 'pk', None)

            choices = [('', '— Pilih Unit —')]
            if ruangan_val:
                try:
                    ru = Ruangan.objects.get(pk=int(ruangan_val))
                    choices.append((ru.nama, ru.nama))
                except Exception:
                    # fallback to full list if ruangan lookup fails
                    units = Unit.objects.all()
                    choices += [(str(u.pk), u.nama) for u in units]
            else:
                units = Unit.objects.all()
                choices += [(str(u.pk), u.nama) for u in units]

            # set Select widget with choices but keep field type as CharField (from model)
            self.fields['unit'].widget = forms.Select(choices=choices, attrs={'class': 'form-control'})

    def save(self, commit=True):
        instance = super().save(commit=False)
        unit_val = self.cleaned_data.get('unit') if hasattr(self, 'cleaned_data') else None
        if unit_val:
            try:
                u = Unit.objects.get(pk=int(unit_val))
                instance.unit = u.nama
            except Exception:
                instance.unit = unit_val
        if commit:
            instance.save()
            self.save_m2m()
        return instance

class DetailSPPBForm(forms.ModelForm):
    class Meta:
        model = DetailSPPB
        fields = ['nama_barang', 'spesifikasi', 'jumlah', 'satuan', 'harga_satuan']
        widgets = {
            'nama_barang': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nama barang'
            }),
            'spesifikasi': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Spesifikasi barang'
            }),
            'jumlah': forms.NumberInput(attrs={'class': 'form-control'}),
            'satuan': forms.TextInput(attrs={
                'class': 'form-control',
                'value': 'Unit'
            }),
            'harga_satuan': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
        }

class UpdateStatusSPPBForm(forms.ModelForm):
    class Meta:
        model = SPPB
        fields = ['status', 'tanggal_datang', 'tanggal_verifikasi', 'catatan']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'tanggal_datang': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'tanggal_verifikasi': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'catatan': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }


class VendorForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = ['nama', 'kontak', 'email', 'alamat']
        widgets = {
            'nama': forms.TextInput(attrs={'class': 'form-control'}),
            'kontak': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'alamat': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }