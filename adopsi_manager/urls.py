from django.urls import path
from .views import (
    view_adopsi,
    create_adopsi,
    detail_adopsi,
    stop_adopsi,
    cancel_adopsi,          # << tambahkan
)

urlpatterns = [
    path('view-adopsi/', view_adopsi, name='view_adopsi'),
    path('create-adopsi/<int:id>/', create_adopsi, name='create_adopsi'),
    path('detail-adopsi/<int:id>/', detail_adopsi, name='detail_adopsi'),
    path('stop-adopsi/<int:id>/', stop_adopsi, name='stop_adopsi'),
    path('cancel-adopsi/<int:id>/', cancel_adopsi, name='cancel_adopsi'),  # << baru
]
