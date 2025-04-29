from django.urls import path
from . import views

app_name = 'manajemen_atraksi'

urlpatterns = [
    # Atraksi URLs
    path('atraksi/', views.atraksi_list, name='atraksi_list'),
    path('atraksi/tambah/', views.atraksi_create, name='atraksi_create'),
    path('atraksi/edit/<str:nama>/', views.atraksi_update, name='atraksi_update'),
    path('atraksi/delete/<str:nama>/', views.atraksi_delete, name='atraksi_delete'),
    
    # Wahana URLs (jika diperlukan)
    path('wahana/', views.wahana_list, name='wahana_list'),
    path('wahana/tambah/', views.wahana_create, name='wahana_create'),
    path('wahana/edit/<str:nama>/', views.wahana_update, name='wahana_update'),
    path('wahana/hapus/<str:nama>/', views.wahana_delete, name='wahana_delete'),


    path('reservasi/<str:role>/', views.reservasi_list, name='reservasi_list'),

    # Create Reservasi
    path('reservasi/create/', views.reservasi_create, name='reservasi_create'),

    # Edit and Delete
    path('reservasi/edit/<str:nama_atraksi>/<str:tanggal>/', views.reservasi_edit, name='reservasi_edit'),
    path('reservasi/delete/<str:nama_atraksi>/<str:tanggal>/', views.reservasi_delete, name='reservasi_delete'),
]

