from django.urls import path
from .views import *

urlpatterns = [
    path('view-satwa/', view_satwa, name='view_satwa'), 
    path('create-satwa/', create_satwa, name='create_satwa'), 
    path('edit-satwa/<int:id>/', edit_satwa, name='edit_satwa'),
    path('view-habitat/', view_habitat, name='view_habitat'),
    path('detail-habitat/<int:id>/', detail_habitat, name='detail_habitat'),
    path('create-habitat/', create_habitat, name='create_habitat'),
    path('edit-habitat/<int:id>/', edit_habitat, name='edit_habitat'),
]