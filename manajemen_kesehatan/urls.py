from django.urls import include, path
from manajemen_kesehatan.views import *

urlpatterns = [
    path('rekam_medis/', view_rekam_medis, name='rekam_medis'),
    path('jadwal_pemeriksaan/', view_jadwal_pemeriksaan, name='jadwal_pemeriksaan'),
]