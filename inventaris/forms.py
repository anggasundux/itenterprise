from django import forms
from .models import Aset, MutasiAset


class AsetForm(forms.ModelForm):
    class Meta:
        model = Aset
        fields = ['kode_aset', 'nama_aset', 'kategori', 'merek', 'nomor_seri', 'ruangan', 'kondisi', 'tanggal_beli', 'keterangan']
        widgets = {
            'kode_aset': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Kode Aset'}),
            'nama_aset': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nama Aset'}),
            'kategori': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Kategori'}),
            'merek': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Merek'}),
            'nomor_seri': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nomor Seri'}),
            'ruangan': forms.Select(attrs={'class': 'form-control'}),
            'kondisi': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('Baik', 'Baik'),
                ('Rusak', 'Rusak'),
                ('Maintenance', 'Maintenance'),
                ('Baru', 'Baru'),
            ]),
            'tanggal_beli': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'keterangan': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Keterangan'}),
        }


class MutasiForm(forms.ModelForm):
    class Meta:
        model = MutasiAset
        fields = ['ke_ruangan']
        widgets = {
            'ke_ruangan': forms.Select(attrs={'class': 'form-control'}),
        }
