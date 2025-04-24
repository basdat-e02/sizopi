from django.urls import path
from .views import (
    view_adopsi,
    create_adopsi,
    detail_adopsi,
    stop_adopsi,
    cancel_adopsi,
    program_adopsi,
    detail_adopsi_adopter,
    laporan_kondisi,
    certificate_adopsi,
    extend_adopsi,
    modal_berhenti_adopter,
    daftar_adopter,
    riwayat_adopsi_adopter,
)

urlpatterns = [
    # staf administrasi
    path('view-adopsi/', view_adopsi, name='view_adopsi'),
    path('create-adopsi/<int:id>/', create_adopsi, name='create_adopsi'),
    path('detail-adopsi/<int:id>/', detail_adopsi, name='detail_adopsi'),
    path('stop-adopsi/<int:id>/', stop_adopsi, name='stop_adopsi'),
    path('cancel-adopsi/<int:id>/', cancel_adopsi, name='cancel_adopsi'),

    # pengunjung / adopter
    path('program-adopsi/', program_adopsi, name='program_adopsi'),
    path('program-adopsi/<int:id>/', detail_adopsi_adopter, name='detail_adopsi_adopter'),
    path('program-adopsi/<int:id>/laporan-kondisi/',laporan_kondisi, name='laporan_kondisi'),
    path('program-adopsi/<int:id>/certificate/', certificate_adopsi, name='certificate_adopsi'),
    path('program-adopsi/<int:id>/extend/', extend_adopsi, name='extend_adopsi'),
    path('program-adopsi/<int:id>/confirm-cancel/', modal_berhenti_adopter, name='modal_berhenti_adopter'),
    
    #RD manajamene riwayat
    path('daftar-adopter/', daftar_adopter, name='daftar_adopter'),
    path('riwayat-adopsi/<str:nama>/', riwayat_adopsi_adopter, name='riwayat_adopsi_adopter'), #http://127.0.0.1:8000/riwayat-adopsi/Ade%20Made/
]

