from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import logout
from functools import wraps
from django.db import connection

# ======================================================================================
# ======================================================================================
#                       IMPORTANT !!!!   SEE ONLY THIS SECTION
# ======================================================================================
# ======================================================================================
#
#
#
#
#
# ======  PILIHAN ROLES DI CASE 2 (SIZOPI)  ======
#
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
#
# 
# ======  DECORATOR FOR AUTHORIZATION  ======
#
#    requirement?
#     - harus ada .env sesuai readme.md
#
#    untuk apa ?
#     - views cuman boleh untuk yg 
#           blm login, 
#           logged in semua role, 
#           logged in dengan role tertentu
#
#    how to use?
#    ***************************************** your views.py  ***********************************
#    *  from main.views import allowed_roles, unauthenticated_user, login_required_custom                    *
#    *
#    *  @unauthenticated_user                                                   
#    *  @allowed_roles(["dokter hewan", "penjaga hewan",]) 
#    *  def your_view(request):                            
#    *      ...                                            
#    *      ...                                            
#    *      ...
#    *  @login_required_custom   
#    *  def your_other_view(request):                            
#    *      ...                                            
#    *      ...                                            
#    *      ...     
#    *
#    *  @login_required_custom
#    *  @allowed_roles(["dokter hewan", "penjaga hewan",])    
#    *  def your_other_other_view(request):                            
#    *      ...                                            
#    *      ...                                            
#    *      ...                                                    
#    *                                                     
#    *******************************************************
def unauthenticated_user(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        # if you have a user in session, kick them out
        if request.session.get('username'):
            return redirect('dashboard')
        # otherwise let them see the view
        return view_func(request, *args, **kwargs)
    return _wrapped

def login_required_custom(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if 'username' not in request.session:
            # send them to your real login page (or however you log people in)
            return redirect('auth_option')
        return view_func(request, *args, **kwargs)
    return _wrapped

def allowed_roles(roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            username = request.session.get('username')
            # at this point we know they're logged in,
            # so session always has a username
            user_role = get_user_role(username)
            if user_role in roles:
                return view_func(request, *args, **kwargs)
            # if they’re logged in but not in an allowed role,
            # send them somewhere safe
            return redirect('dashboard')
        return _wrapped
    return decorator






# ======  PASSING ROLE TO HTML FOR NAVBAR  ======
#
#    requirement?
#     - harus ada .env sesuai readme.md
#
#    untuk apa?
#     - komponen apa aja yang dapat diakses oleh user sesuai dengan ketentuan role nya
#
#    how to use?
#    ******************* your views.py *********************************
#    *  from main.views import get_user_role                           *
#    *                                                                 *
#    *  def yourviews(request):                                        *
#    *      ...                                                        *
#    *      context = {                                                *             
#    *        "role": get_user_role(request.session.get('username'))   *
#    *      }                                                          *
#    *      return render(request, 'your_page.html', context)          *
#    *                                                     *           *
#    *******************************************************************
def get_user_role(username):
    with connection.cursor() as cursor:
        cursor.execute("SELECT get_user_role(%s)", [username])
        result = cursor.fetchone()
        if result:
            return result[0]
        return "unknown"
#
#
#
#
#  ======  SHOW MESSAGE PAGE  ======
#
#   untuk apa?
#    - handle error & warning
#
#   how to use?
#     return redirect(f'/show_message/?msg={message}&type=warning')
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


# ======================================================================================
# ======================================================================================
# ======================================================================================
# ======================================================================================




def check_authentication(request):
    if get_user_role(request.session.get('username')) == "unknown":
         return redirect('auth_option')
    else:
         return redirect('dashboard')

@unauthenticated_user
def auth_option(request):
    context = {
        "role": get_user_role(request.session.get('username'))
    }
    return render(request, 'auth_option.html', context)

@unauthenticated_user
def login_user(request):
    """
    Login:
    - sukses -> redirect ke dashboard
    - gagal -> redirect ke show_message dengan warning
    """
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        if username and password:
            # Call stored function login_user to authenticate
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM login_user(%s, %s)", [username, password])
                user_data = cursor.fetchone()

            if user_data:
                # ✅ Login success
                request.session['username'] = user_data[0]  # username
                request.session.set_expiry(None)  # No expiration

                return redirect("dashboard")  # Redirect to dashboard

            else:
                # ❌ Username atau password salah -> redirect ke show_message
                url = reverse('show_message') + "?type=warning&msg=Username atau Password salah."
                return redirect(url)

        else:
            # ❌ Username atau password kosong -> redirect ke show_message
            url = reverse('show_message') + "?type=warning&msg=Username dan Password wajib diisi."
            return redirect(url)

    # GET request: tampilkan halaman login
    return render(request, "login.html", {"role": "unknown"})

@unauthenticated_user
def choose_register_role(request):
    context = {
        "role": get_user_role(request.session.get('username'))
    }
    return render(request, 'register.html', context)

@unauthenticated_user
def register_pengunjung(request):
    context = {
        "role": get_user_role(request.session.get('username'))
    }
    return render(request, 'register_pengunjung.html', context)

@unauthenticated_user
def register_dokter_hewan(request):
    context = {
        "role": get_user_role(request.session.get('username'))
    }
    return render(request, 'register_dokter_hewan.html', context)

@unauthenticated_user
def register_staff(request):
    context = {
        "role": get_user_role(request.session.get('username'))
    }
    return render(request, 'register_staff.html', context)

def logout_user(request):
    request.session.flush()
    return redirect('login')

@login_required_custom   
def dashboard(request):
    context = {
        "role": get_user_role(request.session.get('username'))
    }
    return render(request, 'dashboard.html', context)

@login_required_custom   
def profile(request):
    context = {
        "role": get_user_role(request.session.get('username'))
    }
    return render(request, 'profile.html', context)

@login_required_custom   
def change_password(request):
    context = {
        "role": get_user_role(request.session.get('username'))
    }
    return render(request, 'change_password.html', context)
