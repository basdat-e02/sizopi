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


    # Reservasi URLs
    path('reservasi/', views.list_reservasi_pengunjung, name='list_reservasi_pengunjung'),
    path('reservasi/form/', views.form_reservasi, name='form_reservasi'),
    path('reservasi/simpan/', views.simpan_reservasi, name='simpan_reservasi'),
    path('reservasi/batalkan/<str:nama_fasilitas>/<str:tanggal>/', views.batalkan_reservasi, name='batalkan_reservasi'),
    path('reservasi/detail/<str:nama_fasilitas>/<str:tanggal>/', views.detail_reservasi, name='detail_reservasi'),
    path('reservasi/edit/<str:nama_fasilitas>/<str:tanggal>/', views.edit_reservasi, name='edit_reservasi'),
    path('reservasi/update/', views.update_reservasi, name='update_reservasi'),
    path('reservasi/konfirmasi_batal/<str:nama_fasilitas>/<str:tanggal>/', views.konfirmasi_batal, name='konfirmasi_batal'),
    # path('reservasi/create/', views.create_reservasi, name='create_reservasi'),


    path('admin/reservasi/', views.list_semua_reservasi, name='list_semua_reservasi'),
    path('admin/reservasi/edit/<str:nama_fasilitas>/<str:tanggal>/', views.edit_status_reservasi, name='edit_status_reservasi'),

]
