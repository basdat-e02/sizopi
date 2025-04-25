from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import logout
import random

# ikutin role yg ini buat nyesuain pilihan-pilihan di navbar
ROLES = [
    # blm login
    "unknown",
    # udah login
    "pengunjung",
    "dokter hewan",
    "penjaga hewan",
    "staf admin",
    "pelatih pertunjukan",
    "pengunjung_adopter",
]

def role_checker(request):
    # TODO : logic ambil role 
    return random.choice(ROLES)


def check_authentication(request):
    # TODO : logic cek seassion, cookies, role user untuk di-redirect bila url kosong
    return redirect('auth_option')

def auth_option(request):
    context = {
        "role": "unknown"
    }
    return render(request, 'auth_option.html', context)

def login_user(request):
    """
    Dummy‑login:
    sukses  -> redirect ke dashboard
    gagal   -> tampilkan login.html + error
    """
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        # cek dua-duanya diisi
        if username and password:
            # 👉 di proyek asli, lakukan authenticate() di sini
            # untuk dummy cukup redirect
            return redirect("dashboard")

        # kalau ada yang kosong, kirim error
        context = {
            "role": "unknown",
            "error": "Username dan Password wajib diisi."
        }
        return render(request, "login.html", context)

    # GET: tampilkan form login kosong
    return render(request, "login.html", {"role": "unknown"})

def choose_register_role(request):
    context = {
        "role": "unknown"
    }
    return render(request, 'register.html', context)

def register_pengunjung(request):
    context = {
        "role": "unknown"
    }
    return render(request, 'register_pengunjung.html', context)

def register_dokter_hewan(request):
    context = {
        "role": "unknown"
    }
    return render(request, 'register_dokter_hewan.html', context)

def register_staff(request):
    context = {
        "role": "unknown"
    }
    return render(request, 'register_staff.html', context)

def logout_user(request):
    logout(request)
    response = HttpResponseRedirect(reverse('auth_option'))
    response.delete_cookie('last_login')
    return response

def dashboard(request):
    context = {
        "role": "pengujung"
    }
    return render(request, 'dashboard.html', context)

def profile(request):
    context = {
        "role": "penjaga hewan"
    }
    return render(request, 'profile.html', context)

def change_password(request):
    context = {
        "role": "pengunjung"
    }
    return render(request, 'change_password.html', context)

# HOW TO USE
# return redirect(f'/show_message/?msg={message}&type=warning')
def show_message(request):
    type = request.GET.get("type", "info")
    msg = request.GET.get("msg", "")

    colors = {
        "success": ("green", "Berhasil"),
        "error": ("red", "Gagal"),
        "warning": ("yellow", "Peringatan"),
    }
    color, text = colors.get(type, ("gray", "Pesan"))

    return render(request, "show_message.html", {
        "message": msg,
        "color": color,
        "text": text
    })


######################################################
##################### PBP ############################
######################################################

# def check_authentication(request):
#     if request.COOKIES == None:
#         return redirect('login')
    
#     response = HttpResponseRedirect(reverse('landing'))
#     response.set_cookie('last_login', str(datetime.datetime.now()))
#     return response

# def login_user(request):
#     next_url = (request.GET.get('next', '/')).replace('-', '_').replace('/','')

#     if request.method == 'POST':
#         form = AuthenticationForm(data=request.POST)

#         if form.is_valid():
#             user = form.get_user()
#             login(request, user)
#             response = HttpResponseRedirect(reverse(next_url))
#             response.set_cookie('last_login', str(datetime.datetime.now()))
#             return response
#         else:
#             messages.error(request, "Invalid username or password. Please try again.")

#     else:
#         form = AuthenticationForm(request)
#     context = {'form': form}
#     return render(request, 'login.html', context)

# # Create your views here.
# def register(request):
#     form = UserCreationForm()

#     if request.method == "POST":
#         form = UserCreationForm(request.POST)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Your account has been successfully created!')
#             return redirect('login')
#     context = {'form':form}
#     return render(request, 'register.html', context)