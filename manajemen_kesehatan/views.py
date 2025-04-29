from django.shortcuts import render

def view_rekam_medis(request):
    return render(request, 'rekam_medis.html')

def view_jadwal_pemeriksaan(request):
    return render(request, 'jadwal_pemeriksaan_kesehatan.html')