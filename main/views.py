from shlex import quote
import uuid
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, resolve_url
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
#
#
#
#
#
#
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
#     - return redirect(f'/show_message/?msg={message}&type=warning')
#           OR/ATAU
#     - return redirect(f'/show_message/?msg={message}&type=success&next_url=view_satwa')
def show_message(request):
    type_     = request.GET.get("type", "info")        # hindari shadowing kata bawaan 'type'
    msg       = request.GET.get("msg", "")
    next_raw  = request.GET.get("next_url")            # bisa None
    next_url  = resolve_url(next_raw) if next_raw else ""

    colors = {
        "success": ("green",  "Berhasil"),
        "error":   ("red",    "Gagal"),
        "warning": ("yellow", "Peringatan"),
    }
    color, text = colors.get(type_, ("gray", "Pesan"))

    return render(request, "show_message.html", {
        "message":  msg,
        "color":    color,
        "text":     text,
        "next_url": next_url,
        "type":     type_,        # ← kirim ke template juga
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
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT * FROM login_user(%s, %s)", [username, password])
                    user_data = cursor.fetchone()              # hanya ada kalau login sukses
            except Exception as e:                            # menangkap RAISE EXCEPTION
                msg = quote(str(e))                           # “Username atau password salah …”
                return redirect(f"{reverse('show_message')}?type=warning&msg={msg}")

            if user_data:
                # ✅ Login success
                request.session['username'] = user_data[0]  # username
                request.session.set_expiry(None)  # No expiration

                message = f"Login Berhasil, Selamat Datang {user_data[0]}!"
                return redirect(f'/show_message/?msg={message}&type=success&next_url=dashboard')

        else:
            # ❌ Username atau password kosong -> redirect ke show_message
            url = reverse('show_message') + "?type=warning&msg=Username dan Password wajib diisi."
            return redirect(url)

    # GET request: tampilkan halaman login
    return render(request, "login.html", {"role": get_user_role(request.session.get('username'))})

@unauthenticated_user
def choose_register_role(request):
    context = {
        "role": get_user_role(request.session.get('username'))
    }
    return render(request, 'register.html', context)

@unauthenticated_user
def register_pengunjung(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '').strip()
        password2 = request.POST.get('password2', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        middle_name = request.POST.get('middle_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        birthdate = request.POST.get('birthdate', '').strip()

        # Validasi basic
        if not all([username, email, password1, password2, first_name, last_name, phone, address, birthdate]):
            msg = quote('Semua bidang harus diisi.')
            return redirect(f"{reverse('show_message')}?type=warning&msg={msg}")
        if password1 != password2:
            msg = quote('Password dan konfirmasi tidak cocok.')
            return redirect(f"{reverse('show_message')}?type=warning&msg={msg}")

        try:
            with connection.cursor() as c:
                c.execute(
                    "SELECT register_pengunjung(%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    [username, email, password1,
                    first_name, middle_name or None, last_name, phone,
                    address, birthdate]
                )
            msg = quote(f"Register berhasil, selamat bergabung {username}!")
            return redirect(f'{reverse("show_message")}?type=success&msg={msg}&next_url=login')
        except Exception as e:
            connection.rollback()          # pastikan transaksi dibersihkan
            # Trigger duplikasi username mengandung kalimat “ERROR: Username ...”
            if 'ERROR: Username' in str(e):
                msg_type = 'warning'       # tampilan kuning, bukan merah
            else:
                msg_type = 'error'
            msg = quote(str(e))
            return redirect(f"{reverse('show_message')}?type={msg_type}&msg={msg}")


    return render(request, 'register_pengunjung.html', {'role': get_user_role(request.session.get('username'))})


@unauthenticated_user
def register_dokter_hewan(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '').strip()
        password2 = request.POST.get('password2', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        middle_name = request.POST.get('middle_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        certification = request.POST.get('certification_number', '').strip()
        spesialisasi_list = request.POST.getlist('spesialisasi')
        spesialisasi_lain = request.POST.get('spesialisasi_lain', '').strip()

        if not all([username, email, password1, password2, first_name, last_name, phone, certification]):
            msg = quote('Semua bidang harus diisi.')
            return redirect(f"{reverse('show_message')}?type=warning&msg={msg}")
        if password1 != password2:
            msg = quote('Password dan konfirmasi tidak cocok.')
            return redirect(f"{reverse('show_message')}?type=warning&msg={msg}")
        
        sp_array = spesialisasi_list[:]          # Django list → Python list
        if 'Lainnya' in sp_array and spesialisasi_lain:
            sp_array.remove('Lainnya')
            sp_array.append(spesialisasi_lain)

        try:
            with connection.cursor() as c:
                c.execute(
                    "SELECT register_dokter_hewan(%s,%s,%s,%s,%s,%s,%s,%s,%s::text[])",
                    [username, email, password1,
                    first_name, middle_name or None, last_name, phone,
                    certification, sp_array]
                )
            message = f"Register berhasil, selamat bergabung {username}!"
            return redirect(f'/show_message/?msg={message}&type=success&next_url=login')
        except Exception as e:
            connection.rollback()          # pastikan transaksi dibersihkan
            # Trigger duplikasi username mengandung kalimat “ERROR: Username ...”
            if 'ERROR: Username' in str(e):
                msg_type = 'warning'       # tampilan kuning, bukan merah
            else:
                msg_type = 'error'
            msg = quote(str(e))
            return redirect(f"{reverse('show_message')}?type={msg_type}&msg={msg}")

    return render(request, 'register_dokter_hewan.html', {'role': get_user_role(request.session.get('username'))})


@unauthenticated_user
def register_staff(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '').strip()
        password2 = request.POST.get('password2', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        middle_name = request.POST.get('middle_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        role_code = request.POST.get('role', '').strip()

        if not all([username, email, password1, password2, first_name, last_name, phone, role_code]):
            msg = quote('Semua bidang harus diisi.')
            return redirect(f"{reverse('show_message')}?type=warning&msg={msg}")
        if password1 != password2:
            msg = quote('Password dan konfirmasi tidak cocok.')
            return redirect(f"{reverse('show_message')}?type=warning&msg={msg}")

        staff_id = str(uuid.uuid4())
        table_map = {
            'PJH': 'PENJAGA_HEWAN',
            'ADM': 'STAF_ADMIN',
            'PLP': 'PELATIH_HEWAN'
        }
        table = table_map.get(role_code)
        if not table:
            msg = quote('Peran staff tidak valid.')
            return redirect(f"{reverse('show_message')}?type=warning&msg={msg}")

        try:
            with connection.cursor() as c:
                c.execute(
                    "SELECT register_staff(%s,%s,%s,%s,%s,%s,%s,%s)",
                    [username, email, password1,
                    first_name, middle_name or None, last_name, phone,
                    role_code]
                )
            message = f"Register berhasil, selamat bergabung {username}!"
            return redirect(f'/show_message/?msg={message}&type=success&next_url=login')
        except Exception as e:
            connection.rollback()          # pastikan transaksi dibersihkan
            # Trigger duplikasi username mengandung kalimat “ERROR: Username ...”
            if 'ERROR: Username' in str(e):
                msg_type = 'warning'       # tampilan kuning, bukan merah
            else:
                msg_type = 'error'
            msg = quote(str(e))
            return redirect(f"{reverse('show_message')}?type={msg_type}&msg={msg}")

    return render(request, 'register_staff.html', {'role': get_user_role(request.session.get('username'))})

def logout_user(request):
    request.session.flush()
    message = f"Logout berhasil, sampai jumpa!"
    return redirect(f'/show_message/?msg={message}&type=success&next_url=login')

@login_required_custom   
def dashboard(request):
    username = request.session['username']
    role = get_user_role(username)

    # Ambil data dasar PENGGUNA
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT nama_depan, nama_tengah, nama_belakang, email, no_telepon
            FROM PENGGUNA
            WHERE username = %s
        """, [username])
        dep, mid, bel, email, phone = cursor.fetchone()
    full_name = f"{dep}{(' ' + mid) if mid else ''} {bel}"

    context = {
        'role':       role,
        'full_name':  full_name,
        'username':   username,
        'email':      email,
        'phone':      phone,
    }

    # Pengunjung & Adopter
    if role in ('pengunjung', 'pengunjung_adopter'):
        with connection.cursor() as cursor:
            cursor.execute("SELECT alamat, tgl_lahir FROM PENGUNJUNG WHERE username_P = %s", [username])
            address, birthdate = cursor.fetchone()
            cursor.execute("SELECT COUNT(*) FROM RESERVASI WHERE username_p = %s", [username])
            visit_count = cursor.fetchone()[0]
            cursor.execute("SELECT COALESCE(SUM(jumlah_tiket),0) FROM RESERVASI WHERE username_p = %s", [username])
            ticket_count = cursor.fetchone()[0]

        context.update({
            'address':      address,
            'birthdate':    birthdate,
            'visit_count':  visit_count,
            'ticket_count': ticket_count,
        })

        if role == 'pengunjung_adopter':
            with connection.cursor() as cursor:
                cursor.execute("SELECT id_adopter FROM ADOPTER WHERE username_adopter = %s", [username])
                row = cursor.fetchone()
                adoptions = []
                if row:
                    cursor.execute("""
                        SELECT he.nama, a.status_pembayaran
                        FROM ADOPSI a
                        JOIN HEWAN he ON a.id_hewan = he.id
                        WHERE a.id_adopter = %s
                    """, [row[0]])
                    adoptions = cursor.fetchall()
            context['adoptions'] = adoptions

    # Dokter Hewan
    if role == 'dokter hewan':
        with connection.cursor() as cursor:
            cursor.execute("SELECT no_str FROM DOKTER_HEWAN WHERE username_DH = %s", [username])
            cert = cursor.fetchone()[0]
            cursor.execute("SELECT nama_spesialisasi FROM SPESIALISASI WHERE username_SH = %s", [username])
            specs = [r[0] for r in cursor.fetchall()]
            cursor.execute("SELECT COUNT(DISTINCT id_hewan) FROM CATATAN_MEDIS WHERE username_dh = %s", [username])
            handled = cursor.fetchone()[0]

        context.update({
            'certification':   cert,
            'specializations': specs,
            'handled_count':   handled,
        })

    # Penjaga Hewan
    if role == 'penjaga hewan':
        with connection.cursor() as cursor:
            cursor.execute("SELECT id_staf FROM PENJAGA_HEWAN WHERE username_jh = %s", [username])
            staff_id = cursor.fetchone()[0]
            cursor.execute("""
                SELECT COUNT(*) FROM PAKAN
                WHERE id_hewan IN (
                  SELECT id_hewan FROM MEMBERI WHERE username_jh = %s
                )
                AND DATE(jadwal) = CURRENT_DATE
            """, [username])
            fed_count = cursor.fetchone()[0]

        context.update({
            'staff_id': staff_id,
            'fed_count': fed_count,
        })

    # Staf Administrasi
    if role == 'staf admin':
        with connection.cursor() as cursor:
            cursor.execute("SELECT id_staf FROM STAF_ADMIN WHERE username_sa = %s", [username])
            staff_id = cursor.fetchone()[0]
            cursor.execute("SELECT COALESCE(SUM(jumlah_tiket),0) FROM RESERVASI WHERE tanggal_kunjungan = CURRENT_DATE")
            sales_today = cursor.fetchone()[0]
            revenue_today = sales_today * 100000  # asumsikan harga per tiket 100k
            cursor.execute("SELECT COUNT(DISTINCT username_p) FROM RESERVASI WHERE tanggal_kunjungan = CURRENT_DATE")
            visitor_count = cursor.fetchone()[0]
            cursor.execute("""
                SELECT COALESCE(SUM(jumlah_tiket * 100000),0)
                FROM RESERVASI
                WHERE tanggal_kunjungan >= CURRENT_DATE - INTERVAL '7 days'
            """)
            weekly_revenue = cursor.fetchone()[0]

        context.update({
            'staff_id':      staff_id,
            'sales_today':   sales_today,
            'revenue_today': revenue_today,
            'visitor_count': visitor_count,
            'weekly_revenue': weekly_revenue,
        })

    # Pelatih Pertunjukan
    if role == 'pelatih pertunjukan':
        with connection.cursor() as cursor:
            cursor.execute("SELECT id_staf FROM PELATIH_HEWAN WHERE username_lh = %s", [username])
            staff_id = cursor.fetchone()[0]
            # Ambil jadwal hari ini
            cursor.execute(
                """
                SELECT TO_CHAR(tgl_penugasan, 'HH24:MI') || ' ' || nama_atraksi
                FROM JADWAL_PENUGASAN
                WHERE username_lh = %s
                  AND DATE(tgl_penugasan) = CURRENT_DATE
                """, [username])
            rows = cursor.fetchall()
            show_schedule = ', '.join(r[0] for r in rows) or 'Tidak ada'
            # Hitung jumlah penugasan
            cursor.execute("SELECT COUNT(*) FROM JADWAL_PENUGASAN WHERE username_lh = %s", [username])
            trained_count = cursor.fetchone()[0]
            # Status latihan terakhir
            cursor.execute(
                """
                SELECT TO_CHAR(MAX(tgl_penugasan), 'YYYY-MM-DD HH24:MI')
                FROM JADWAL_PENUGASAN
                WHERE username_lh = %s
                """, [username])
            last_training_status = cursor.fetchone()[0] or 'Belum ada'
        context.update({
            'staff_id': staff_id,
            'show_schedule': show_schedule,
            'trained_count': trained_count,
            'last_training_status': last_training_status,
        })


    return render(request, 'dashboard.html', context)

@login_required_custom   
def profile(request):
    username = request.session.get('username')
    role = get_user_role(username)

    if request.method == 'POST':
        # Ambil data dasar
        email       = request.POST.get('email', '').strip()
        first_name  = request.POST.get('first_name', '').strip()
        middle_name = request.POST.get('middle_name', '').strip()
        last_name   = request.POST.get('last_name', '').strip()
        phone       = request.POST.get('phone', '').strip()
        # Role-specific POST
        address     = request.POST.get('address', '').strip() if role == 'pengunjung' else None
        birthdate   = request.POST.get('birthdate', '').strip() if role == 'pengunjung' else None
        specs       = request.POST.getlist('specializations') if role == 'dokter hewan' else []
        specs_other = request.POST.get('specializations_other', '').strip() if role == 'dokter hewan' else ''

        # Validasi minimal
        if not all([email, first_name, last_name, phone]):
            msg = quote('Email, nama depan, nama belakang, dan telepon wajib diisi.')
            return redirect(f"{reverse('show_message')}?type=warning&msg={msg}")

        try:
            with connection.cursor() as cursor:
                # Update PENGGUNA
                cursor.execute(
                    """
                    UPDATE PENGGUNA
                       SET email=%s,
                           nama_depan=%s,
                           nama_tengah=%s,
                           nama_belakang=%s,
                           no_telepon=%s
                     WHERE username=%s
                    """,
                    [email, first_name, middle_name or None, last_name, phone, username]
                )
                # Update Pengunjung
                if role == 'pengunjung':
                    cursor.execute(
                        "UPDATE PENGUNJUNG SET alamat=%s, tgl_lahir=%s WHERE username_P=%s",
                        [address, birthdate, username]
                    )
                # Update Dokter Hewan spesialisasi
                if role == 'dokter hewan':
                    cursor.execute("DELETE FROM SPESIALISASI WHERE username_SH=%s", [username])
                    for sp in specs:
                        cursor.execute(
                            "INSERT INTO SPESIALISASI(username_SH, nama_spesialisasi) VALUES (%s, %s)",
                            [username, sp]
                        )
                    if specs_other:
                        cursor.execute(
                            "INSERT INTO SPESIALISASI(username_SH, nama_spesialisasi) VALUES (%s, %s)",
                            [username, specs_other]
                        )
            message = f"Profile berhasil diperbarui!"
            return redirect(f'/show_message/?msg={message}&type=success&next_url=profile')

        except Exception as e:
            msg = quote(str(e))
            return redirect(f"{reverse('show_message')}?type=error&msg={msg}")

    # GET: load data
    data = {'role': role, 'username': username}
    with connection.cursor() as cursor:
        # Basic PENGGUNA
        cursor.execute(
            "SELECT email, nama_depan, nama_tengah, nama_belakang, no_telepon FROM PENGGUNA WHERE username=%s",
            [username]
        )
        email, dep, mid, bel, phone = cursor.fetchone()
        data.update({
            'email': email,
            'first_name': dep,
            'middle_name': mid or '',
            'last_name': bel,
            'phone': phone,
        })

        # Role-specific GET
        if role == 'pengunjung':
            cursor.execute("SELECT alamat, tgl_lahir FROM PENGUNJUNG WHERE username_P=%s", [username])
            addr, born = cursor.fetchone()
            data.update({'address': addr, 'birthdate': born})

        elif role == 'dokter hewan':
            # Sertifikasi
            cursor.execute("SELECT no_str FROM DOKTER_HEWAN WHERE username_DH=%s", [username])
            data['certification'] = cursor.fetchone()[0]
            # Spesialisasi
            cursor.execute("SELECT nama_spesialisasi FROM SPESIALISASI WHERE username_SH=%s", [username])
            specs = [r[0] for r in cursor.fetchall()]
            defaults = ['Mamalia Besar', 'Reptil', 'Burung Eksotis', 'Primata']
            data['specializations'] = [s for s in specs if s in defaults]
            other = [s for s in specs if s not in defaults]
            data['specializations_other'] = other[0] if other else ''

        elif role in ('penjaga hewan', 'staf admin', 'pelatih pertunjukan'):
            table_map = {
                'penjaga hewan': ('PENJAGA_HEWAN','username_jh'),
                'staf admin':    ('STAF_ADMIN','username_sa'),
                'pelatih pertunjukan':('PELATIH_HEWAN','username_lh'),
            }
            table, usercol = table_map[role]
            cursor.execute(
                f"SELECT id_staf FROM {table} WHERE {usercol}=%s",
                [username]
            )
            data['staff_id'] = cursor.fetchone()[0]

    return render(request, 'profile.html', data)

@login_required_custom   
def change_password(request):
    username = request.session.get('username')
    if request.method == 'POST':
        old_pw = request.POST.get('old_password', '').strip()
        new_pw1 = request.POST.get('new_password1', '').strip()
        new_pw2 = request.POST.get('new_password2', '').strip()

        if not all([old_pw, new_pw1, new_pw2]):
            msg = quote('Semua bidang password wajib diisi.')
            return redirect(f"{reverse('show_message')}?type=warning&msg={msg}")
        if new_pw1 != new_pw2:
            msg = quote('Password baru dan konfirmasi tidak cocok.')
            return redirect(f"{reverse('show_message')}?type=warning&msg={msg}")
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM login_user(%s, %s)", [username, old_pw])
                if not cursor.fetchone():
                    msg = quote('Password lama salah.')
                    return redirect(f"{reverse('show_message')}?type=warning&msg={msg}")
                cursor.execute("UPDATE PENGGUNA SET password=%s WHERE username=%s", [new_pw1, username])
            message = f"Password berhasil diperbarui!"
            return redirect(f'/show_message/?msg={message}&type=success&next_url=profile')
        except Exception as e:
            msg = quote(str(e))
            return redirect(f"{reverse('show_message')}?type=error&msg={msg}")

    return render(request, 'change_password.html', {'role': get_user_role(username)})
