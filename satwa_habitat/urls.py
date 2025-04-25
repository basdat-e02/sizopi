from django.urls import path
from .views import *

urlpatterns = [
    path('view-satwa/', view_satwa, name='view_satwa'), 
    path('create-satwa/', create_satwa, name='create_satwa'), 
    path('edit-satwa/<str:uuid>/', edit_satwa, name='edit_satwa'),
    path('view-habitat/', view_habitat, name='view_habitat'),
    path('detail-habitat/<str:nama>/', detail_habitat, name='detail_habitat'),
    path('create-habitat/', create_habitat, name='create_habitat'),
    path('edit-habitat/<str:nama>/', edit_habitat, name='edit_habitat'),
]