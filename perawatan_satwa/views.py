from django.shortcuts import render

def view_pemberian_pakan(request):
    return render(request, 'pemberian_pakan.html')

def view_riwayat_pemberian_pakan(request):
    return render(request, 'riwayat_pemberian_pakan.html')

