from django.urls import path
from .views import *

urlpatterns = [
    path('', check_authentication, name=''), 
    path('auth-option/', auth_option, name='auth_option'),
    path('login/', login_user, name='login'), 
    path('register/', choose_register_role, name='register'), 
    path('register/pengunjung/', register_pengunjung, name='register_pengunjung'),
    path('register/dokter-hewan/', register_dokter_hewan, name='register_dokter_hewan'),
    path('register/staff/', register_staff, name='register_staff'),
    path('logout/', logout_user, name='logout'),
    path('dashboard', dashboard, name='dashboard'),
    path('profile', profile, name='profile'),
    path('change-password', change_password, name='change_password'),
]
