from django.shortcuts import render
from .models import JadwalPemeliharaan

def pemeliharaan_list(request):
    data = JadwalPemeliharaan.objects.all()
    return render(request, 'pemeliharaan/list.html', {
        'data': data
    })
