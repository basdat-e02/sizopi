from django.urls import path
from .views import (
    # Admin
    view_adopsi, pendataan_adopter, detail_adopsi, edit_adopsi,
    stop_adopsi, cancel_adopsi,
    # Pengunjung/Adopter
    program_adopsi, detail_adopsi_adopter, laporan_kondisi,
    certificate_adopsi, extend_adopsi, modal_berhenti_adopter,
    # Statistik & Riwayat
    daftar_adopter, riwayat_adopsi_adopter,
)

urlpatterns = [
    # — Admin — #
    path('view-adopsi/', view_adopsi, name='view_adopsi'),
    path('pendataan-adopter/<uuid:id_hewan>/', pendataan_adopter, name='pendataan_adopter'),
    path('detail-adopsi/<uuid:id_adopter>/<uuid:id_hewan>/<slug:tgl_mulai_adopsi>/',
         detail_adopsi, name='detail_adopsi'),
    path('edit-adopsi/<uuid:id_adopter>/<uuid:id_hewan>/<slug:tgl_mulai_adopsi>/',
         edit_adopsi, name='edit_adopsi'),
    path('stop-adopsi/<uuid:id_adopter>/<uuid:id_hewan>/<slug:tgl_mulai_adopsi>/',
         stop_adopsi, name='stop_adopsi'),
    path('cancel-adopsi/<uuid:id_adopter>/<uuid:id_hewan>/<slug:tgl_mulai_adopsi>/',
         cancel_adopsi, name='cancel_adopsi'),

    # — Pengunjung/Adopter — #
    path('program-adopsi/', program_adopsi, name='program_adopsi'),
    path('program-adopsi/<uuid:id_adopter>/<uuid:id_hewan>/<slug:tgl_mulai_adopsi>/',
         detail_adopsi_adopter, name='detail_adopsi_adopter'),
    path('program-adopsi/<uuid:id_adopter>/<uuid:id_hewan>/<slug:tgl_mulai_adopsi>/laporan-kondisi/',
         laporan_kondisi, name='laporan_kondisi'),
    path('program-adopsi/<uuid:id_adopter>/<uuid:id_hewan>/<slug:tgl_mulai_adopsi>/certificate/',
         certificate_adopsi, name='certificate_adopsi'),
    path('program-adopsi/<uuid:id_adopter>/<uuid:id_hewan>/<slug:tgl_mulai_adopsi>/extend/',
         extend_adopsi, name='extend_adopsi'),
    path('program-adopsi/<uuid:id_adopter>/<uuid:id_hewan>/<slug:tgl_mulai_adopsi>/confirm-cancel/',
         modal_berhenti_adopter, name='modal_berhenti_adopter'),

    # — Statistik & Riwayat — #
    path('daftar-adopter/', daftar_adopter, name='daftar_adopter'),
    path('riwayat-adopsi/<uuid:id_adopter>/', riwayat_adopsi_adopter, name='riwayat_adopsi_adopter'),
]
