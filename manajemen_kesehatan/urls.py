from django.urls import include, path
from manajemen_kesehatan.views import *

urlpatterns = [
    path('rekam_medis/', view_rekam_medis, name='rekam_medis'),
    # path untuk fungsi UPDATE dan DELETE rekam medis
    path('update_rekam_medis/', update_rekam_medis, name='update_rekam_medis'),
    path('delete_rekam_medis/', delete_rekam_medis, name='delete_rekam_medis'),
    path('jadwal_pemeriksaan/', view_jadwal_pemeriksaan, name='jadwal_pemeriksaan'),
    #  path untuk fungsi UPDATE dan DELETE rekam medis
    path('update_jadwal_pemeriksaan/', update_jadwal_pemeriksaan, name='update_jadwal_pemeriksaan'),
    path('delete_jadwal_pemeriksaan/', delete_jadwal_pemeriksaan, name='delete_jadwal_pemeriksaan'),
    # klo ada view 'profile' sbrnya gatau si buat apa ini
    path('profile/', profile, name='profile'), 
]