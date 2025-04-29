from django.urls import include, path
from perawatan_satwa.views import *

urlpatterns = [
    path('pemberian-pakan/', view_pemberian_pakan, name='pemberian_pakan'),
    path('riwayat-pemberian-pakan/', view_riwayat_pemberian_pakan, name='riwayat_pemberian_pakan'),
]

