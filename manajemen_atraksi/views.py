from email.utils import parsedate
from pyexpat.errors import messages
from django.shortcuts import render, redirect
from django.db import transaction
from django.db import connection
from main.views import allowed_roles, login_required_custom

def execute_query(query, params=None, fetch=False):
    with connection.cursor() as cursor:
        cursor.execute(query, params or [])
        if fetch:
            columns = [col[0] for col in cursor.description]
            return [
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ]
        return cursor.rowcount

def get_pelatih_list():
    query = "SELECT username_lh FROM PELATIH_HEWAN;"

    return execute_query(query, fetch=True)



def get_hewan_list():
    query = "SELECT id, nama FROM hewan"
    hewan_list = execute_query(query, fetch=True)
    print(hewan_list)  # cek output
    return hewan_list



def get_pelatih_choices():
    with connection.cursor() as cursor:
        cursor.execute("SELECT username_lh FROM PELATIH_HEWAN")
        result = cursor.fetchall()
    # Convert the result (list of tuples) to a list of strings
    return [item[0] for item in result]

def get_hewan_choices():
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, nama_hewan FROM HEWAN")
        result = cursor.fetchall()
    return [(row[0], row[1]) for row in result]  # Ambil ID dan nama hewan
def get_atraksi_by_nama(nama):
    query = """
    SELECT 
        a.nama_atraksi AS nama,
        a.lokasi,
        f.jadwal,
        f.kapasitas_max AS kapasitas,
        jp.username_lh AS pelatih
    FROM atraksi a
    JOIN fasilitas f ON a.nama_atraksi = f.nama
    LEFT JOIN jadwal_penugasan jp ON a.nama_atraksi = jp.nama_atraksi
    WHERE a.nama_atraksi = %s
    LIMIT 1
    """
    result = execute_query(query, [nama], fetch=True)
    return result[0] if result else None

def get_hewan_by_atraksi(nama):
    query = """
    SELECT id_hewan 
    FROM berpartisipasi 
    WHERE nama_fasilitas = %s
    """
    result = execute_query(query, [nama], fetch=True)
    return [row['id_hewan'] for row in result]
@login_required_custom
@allowed_roles(["staf admin"])
def atraksi_list(request):
    query = """
    SELECT 
        a.nama_atraksi AS nama,
        a.lokasi,
        f.jadwal,
        f.kapasitas_max AS kapasitas,
        STRING_AGG(DISTINCT ph.username_lh, ', ') AS pelatih,
        STRING_AGG(DISTINCT h.nama, ', ') AS hewan
    FROM atraksi a
    JOIN fasilitas f ON a.nama_atraksi = f.nama
    LEFT JOIN jadwal_penugasan jp ON a.nama_atraksi = jp.nama_atraksi
    LEFT JOIN pelatih_hewan ph ON jp.username_lh = ph.username_lh
    LEFT JOIN pengguna p ON ph.username_lh = p.username
    LEFT JOIN berpartisipasi bp ON f.nama = bp.nama_fasilitas
    LEFT JOIN hewan h ON bp.id_hewan = h.id
    GROUP BY a.nama_atraksi, a.lokasi, f.jadwal, f.kapasitas_max
    """
    atraksi_list = execute_query(query, fetch=True)
    
    return render(request, 'atraksi_list.html', {
        "atraksi_list": atraksi_list,
    })
@login_required_custom
@allowed_roles(["staf admin"])
@transaction.atomic
def atraksi_create(request):
    if request.method == 'POST':
        try:
            # Ambil nilai dari form POST
            nama = request.POST.get('nama')
            jadwal = request.POST.get('jadwal')
            kapasitas = request.POST.get('kapasitas')
            lokasi = request.POST.get('lokasi')
            pelatih = request.POST.getlist('pelatih')
            hewan_ids = request.POST.getlist('hewan')
            # 1. Insert ke FASILITAS
            query_fasilitas = """
            INSERT INTO fasilitas (nama, jadwal, kapasitas_max)
            VALUES (%s, %s, %s)
            """
            execute_query(query_fasilitas, [nama, jadwal, kapasitas])
            
            # 2. Insert ke ATRAKSI
            query_atraksi = """
            INSERT INTO atraksi (nama_atraksi, lokasi)
            VALUES (%s, %s)
            """
            execute_query(query_atraksi, [nama, lokasi])
            
 # 3. Update pelatih
            execute_query(
                "DELETE FROM jadwal_penugasan WHERE nama_atraksi = %s", 
                [nama]
            )
            if pelatih:
                for username in pelatih:
                    if username:
                        # Simpan jumlah penugasan sebelum insert
                        before = execute_query(
                            "SELECT COUNT(*) FROM jadwal_penugasan WHERE username_lh = %s AND nama_atraksi = %s",
                            [username, nama],
                            fetch=True
                        )[0]['count']
                        
                        # Coba insert
                        execute_query(
                            "INSERT INTO jadwal_penugasan (username_lh, tgl_penugasan, nama_atraksi) VALUES (%s, NOW(), %s)",
                            [username, nama]
                        )
                        
                        # Cek apakah benar-benar masuk
                        after = execute_query(
                            "SELECT COUNT(*) FROM jadwal_penugasan WHERE username_lh = %s AND nama_atraksi = %s",
                            [username, nama],
                            fetch=True
                        )[0]['count']
                        
                        if after == before:
                            messages.warning(request, f"Pelatih {username} tidak ditambahkan karena sudah bertugas lebih dari 3 bulan di atraksi ini.")
            print(request.POST)
            print(request.POST.getlist('hewan'))

            
            # 4. Update hewan
            execute_query(
                "DELETE FROM berpartisipasi WHERE nama_fasilitas = %s", 
                [nama]
            )
            for hewan_id in hewan_ids:
                if hewan_id:  
                    execute_query(
            "INSERT INTO berpartisipasi (nama_fasilitas, id_hewan) VALUES (%s, %s)",
                        [nama, hewan_id]
                    )
            
            # Jika semua query berhasil, redirect ke daftar atraksi
            return redirect('manajemen_atraksi:atraksi_list')
            
        except Exception as e:
            # Tangkap error dan tampilkan ke pengguna
            return render(request, 'atraksi_form.html', {
                "error": str(e),
                "action": "Tambah",
                "pelatih_list": get_pelatih_list(),
                "hewan_list": get_hewan_list(),
            })
    
    # Jika bukan POST, tampilkan halaman form untuk tambah atraksi
    return render(request, 'atraksi_form.html', {
        "action": "Tambah",
        "pelatih_list": get_pelatih_list(),
        "hewan_list": get_hewan_list(),
    })
@login_required_custom
@allowed_roles(["staf admin"])
@transaction.atomic
def atraksi_update(request, nama):
    if request.method == 'POST':
        lokasi = request.POST.get('lokasi')
        kapasitas = request.POST.get('kapasitas')
        jadwal = request.POST.get('jadwal')
        pelatih = request.POST.getlist('pelatih')
        hewan_ids = request.POST.getlist('hewan')
        
        try:
            # 1. Update FASILITAS
            query_fasilitas = """
            UPDATE fasilitas 
            SET jadwal = %s, kapasitas_max = %s
            WHERE nama = %s
            """
            execute_query(query_fasilitas, [jadwal, kapasitas, nama])
            
            # 2. Update ATRAKSI
            query_atraksi = """
            UPDATE atraksi 
            SET lokasi = %s
            WHERE nama_atraksi = %s
            """
            execute_query(query_atraksi, [lokasi, nama])
            
            # 3. Update pelatih
            execute_query(
                "DELETE FROM jadwal_penugasan WHERE nama_atraksi = %s", 
                [nama]
            )
            if pelatih:
                for username in pelatih:
                    if username:
                        # Simpan jumlah penugasan sebelum insert
                        before = execute_query(
                            "SELECT COUNT(*) FROM jadwal_penugasan WHERE username_lh = %s AND nama_atraksi = %s",
                            [username, nama],
                            fetch=True
                        )[0]['count']
                        
                        # Coba insert
                        execute_query(
                            "INSERT INTO jadwal_penugasan (username_lh, tgl_penugasan, nama_atraksi) VALUES (%s, NOW(), %s)",
                            [username, nama]
                        )
                        
                        # Cek apakah benar-benar masuk
                        after = execute_query(
                            "SELECT COUNT(*) FROM jadwal_penugasan WHERE username_lh = %s AND nama_atraksi = %s",
                            [username, nama],
                            fetch=True
                        )[0]['count']
                        
                        if after == before:
                            messages.warning(request, f"Pelatih {username} tidak ditambahkan karena sudah bertugas lebih dari 3 bulan di atraksi ini.")
            print(request.POST)
            print(request.POST.getlist('hewan'))

            
            # 4. Update hewan
            execute_query(
                "DELETE FROM berpartisipasi WHERE nama_fasilitas = %s", 
                [nama]
            )
            for hewan_id in hewan_ids:
                if hewan_id:  
                    execute_query(
            "INSERT INTO berpartisipasi (nama_fasilitas, id_hewan) VALUES (%s, %s)",
                        [nama, hewan_id]
                    )

            
            return redirect('manajemen_atraksi:atraksi_list')
            
        except Exception as e:
            atraksi = get_atraksi_by_nama(nama)
            atraksi['hewan_terlibat'] = get_hewan_by_atraksi(nama)
            return render(request, 'atraksi_form.html', {
                "error": str(e),
                "atraksi": atraksi,
                "action": "Edit",
                "pelatih_list": get_pelatih_list(),
                "hewan_list": get_hewan_list(),
            })
    
    atraksi = get_atraksi_by_nama(nama)
    atraksi['hewan_terlibat'] = get_hewan_by_atraksi(nama)
    
    return render(request, 'atraksi_form.html', {
        "atraksi": atraksi,
        "action": "Edit",
        "pelatih_list": get_pelatih_list(),
        "hewan_list": get_hewan_list(),
    })

@login_required_custom
@allowed_roles(["staf admin"])
@transaction.atomic
def atraksi_delete(request, nama):
    if request.method == 'POST':
        try:
            with transaction.atomic():  # Menggunakan atomic block untuk menjaga konsistensi
                # 1. Hapus terlebih dahulu dari BERPARTISIPASI
                execute_query("DELETE FROM berpartisipasi WHERE nama_fasilitas = %s", [nama])

                # 2. Hapus dari JADWAL_PENUGASAN
                execute_query("DELETE FROM jadwal_penugasan WHERE nama_atraksi = %s", [nama])

                # 3. Hapus dari ATRAKSI
                execute_query("DELETE FROM atraksi WHERE nama_atraksi = %s", [nama])

                # 4. Hapus dari FASILITAS
                execute_query("DELETE FROM fasilitas WHERE nama = %s", [nama])

            # Jika semua query berhasil, redirect ke daftar atraksi
            return redirect('manajemen_atraksi:atraksi_list')

        except Exception as e:
            print(f"Error: {e}")  # Menampilkan error ke log atau console
            atraksi = get_atraksi_by_nama(nama)
            return render(request, 'atraksi_confirm_delete.html', {
                "error": str(e),
                "atraksi": atraksi,
            })

    # Jika bukan POST, tampilkan halaman konfirmasi penghapusan
    atraksi = get_atraksi_by_nama(nama)
    return render(request, 'atraksi_confirm_delete.html', {
        "atraksi": atraksi,
    })



@login_required_custom
@allowed_roles(["staf admin"])
def wahana_list(request):
    query = """
    SELECT 
        w.nama_wahana AS nama,
        f.jadwal,
        f.kapasitas_max AS kapasitas,
        w.peraturan
    FROM wahana w
    JOIN fasilitas f ON w.nama_wahana = f.nama
    """
    wahana_list = execute_query(query, fetch=True)
    
    # Split 'peraturan' into a list for each wahana
    for wahana in wahana_list:
        wahana['peraturan'] = wahana['peraturan'].split(",") if wahana['peraturan'] else []

    return render(request, 'wahana_list.html', {
        "wahana_list": wahana_list,
    })


@transaction.atomic
def wahana_create(request):
    if request.method == 'POST':
        nama = request.POST.get('nama')
        kapasitas = request.POST.get('kapasitas')
        jadwal = request.POST.get('jadwal')
        peraturan_list = request.POST.getlist('peraturan')
        peraturan = '. '.join([p.strip() for p in peraturan_list if p.strip()])
        
        try:
            # 1. Insert ke FASILITAS
            query_fasilitas = """
            INSERT INTO fasilitas (nama, jadwal, kapasitas_max)
            VALUES (%s, %s, %s)
            """
            execute_query(query_fasilitas, [nama, jadwal, kapasitas])
            
            # 2. Insert ke WAHANA
            query_wahana = """
            INSERT INTO wahana (nama_wahana, peraturan)
            VALUES (%s, %s)
            """
            execute_query(query_wahana, [nama, peraturan])
            
            return redirect('manajemen_atraksi:wahana_list')
            
        except Exception as e:
            return render(request, 'wahana_form.html', {
                "error": str(e),
                "action": "Tambah",
            })
    
    return render(request, 'wahana_form.html', {
        "action": "Tambah",
    })

@login_required_custom
@allowed_roles(["staf admin"])
@transaction.atomic
def wahana_update(request, nama):
    if request.method == 'POST':
        kapasitas = request.POST.get('kapasitas')
        jadwal = request.POST.get('jadwal')
        peraturan_list = request.POST.getlist('peraturan')
        peraturan = '. '.join([p.strip() for p in peraturan_list if p.strip()])

        
        try:
            # 1. Update FASILITAS
            query_fasilitas = """
            UPDATE fasilitas 
            SET jadwal = %s, kapasitas_max = %s
            WHERE nama = %s
            """
            execute_query(query_fasilitas, [jadwal, kapasitas, nama])
            
            # 2. Update WAHANA
            query_wahana = """
            UPDATE wahana 
            SET peraturan = %s
            WHERE nama_wahana = %s
            """
            execute_query(query_wahana, [peraturan, nama])
            
            return redirect('manajemen_atraksi:wahana_list')
            
        except Exception as e:
            wahana = get_wahana_by_nama(nama)
            return render(request, 'wahana_form.html', {
                "error": str(e),
                "wahana": wahana,
                "action": "Edit",
            })
    
    wahana = get_wahana_by_nama(nama)
    return render(request, 'wahana_form.html', {
        "wahana": wahana,
        "action": "Edit",
    })

@login_required_custom
@allowed_roles(["staf admin"])
@transaction.atomic
def wahana_delete(request, nama):
    if request.method == 'POST':
        try:
            # 1. Hapus dari WAHANA
            execute_query("DELETE FROM wahana WHERE nama_wahana = %s", [nama])
            
            # 2. Hapus dari FASILITAS
            execute_query("DELETE FROM fasilitas WHERE nama = %s", [nama])
            
            return redirect('manajemen_atraksi:wahana_list')
            
        except Exception as e:
            wahana = get_wahana_by_nama(nama)
            return render(request, 'wahana_confirm_delete.html', {
                "error": str(e),
                "wahana": wahana,
            })
    
    wahana = get_wahana_by_nama(nama)
    return render(request, 'wahana_confirm_delete.html', {
        "wahana": wahana,
    })

def get_wahana_by_nama(nama):
    query = """
    SELECT 
        w.nama_wahana AS nama,
        f.jadwal,
        f.kapasitas_max AS kapasitas,
        w.peraturan
    FROM wahana w
    JOIN fasilitas f ON w.nama_wahana = f.nama
    WHERE w.nama_wahana = %s
    """
    result = execute_query(query, [nama], fetch=True)
    return result[0] if result else None







#=========================================================================================================================#


from django.db import connection
from main.views import allowed_roles, login_required_custom


@login_required_custom
@allowed_roles(['pengunjung','pengunjung_adopter'])
def list_reservasi_pengunjung(request):
    username = request.session.get("username")

    # Ambil reservasi milik pengunjung
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT r.nama_fasilitas, f.jadwal, r.jumlah_tiket, r.status, f,tanggal_kunjungan
            FROM RESERVASI r
            JOIN FASILITAS f ON r.nama_fasilitas = f.nama
            WHERE r.username_p = %s
            ORDER BY r.tanggal_kunjungan DESC
        """, [username])
        reservasi_saya = cursor.fetchall()

    # Ambil semua atraksi + kapasitas tersisa
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                f.nama, 
                f.jadwal,
                (f.kapasitas_max - COALESCE(SUM(r.jumlah_tiket), 0)) AS sisa_kapasitas,
                f.kapasitas_max
            FROM FASILITAS f
            JOIN ATRAKSI a ON f.nama = a.nama_atraksi
            LEFT JOIN RESERVASI r ON f.nama = r.nama_fasilitas AND r.status != 'Dibatalkan'
            GROUP BY f.nama, f.jadwal, f.kapasitas_max
            ORDER BY f.jadwal ASC
        """)
        reservasi_tersedia = cursor.fetchall()

    context = {
        "reservasi_saya": reservasi_saya,
        "reservasi_tersedia": reservasi_tersedia,
    }

    return render(request, 'list_reservasi_pengunjung.html', context)

from django.utils.dateparse import parse_date

@login_required_custom
@allowed_roles(['pengunjung','pengunjung_adopter'])
def detail_reservasi(request, nama_fasilitas, tanggal):
    username = request.session.get("username")
    tanggal_kunjungan = parse_date(tanggal)  # convert dari string ke date object

    if not tanggal_kunjungan:
        print("❌ Format tanggal tidak valid:", tanggal)
        return redirect('manajemen_atraksi:list_reservasi_pengunjung')

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT r.nama_fasilitas, r.tanggal_kunjungan, r.jumlah_tiket, r.status, f.jadwal
            FROM RESERVASI r
            JOIN FASILITAS f ON r.nama_fasilitas = f.nama
            WHERE r.username_p = %s
            AND r.nama_fasilitas = %s
            AND r.tanggal_kunjungan = %s
        """, [username, nama_fasilitas, tanggal_kunjungan])
        detail = cursor.fetchone()

    if not detail:
        print("❌ Reservasi tidak ditemukan:", nama_fasilitas, tanggal)
        return redirect('manajemen_atraksi:list_reservasi_pengunjung')

    context = {
        "reservasi": detail  # [nama_fasilitas, tanggal_kunjungan, jumlah_tiket, status, jadwal_fasilitas]
    }
    return render(request, 'detail_reservasi.html', context)

from urllib.parse import unquote
from datetime import datetime
@login_required_custom
@allowed_roles(['pengunjung','pengunjung_adopter'])
def edit_reservasi(request, nama_fasilitas, tanggal):
    username = request.session.get("username")

    # Decode fasilitas dan parse tanggal
    nama_fasilitas = unquote(nama_fasilitas)
    try:
        tanggal_obj = datetime.strptime(tanggal, "%Y-%m-%d").date()
    except ValueError:
        print("❌ Format tanggal tidak valid:", tanggal)
        return redirect('manajemen_atraksi:list_reservasi_pengunjung')

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT r.nama_fasilitas, r.tanggal_kunjungan, r.jumlah_tiket
            FROM RESERVASI r
            WHERE r.username_p = %s 
            AND r.nama_fasilitas = %s 
            AND r.tanggal_kunjungan = %s
        """, [username, nama_fasilitas, tanggal_obj])

        reservasi = cursor.fetchone()

        if reservasi is None:
            print("❌ Reservasi tidak ditemukan:", nama_fasilitas, tanggal)
            return redirect('manajemen_atraksi:list_reservasi_pengunjung')

        cursor.execute("""
            SELECT a.nama_atraksi
            FROM ATRAKSI a
            JOIN FASILITAS f ON a.nama_atraksi = f.nama
        """)
        wahana_list = cursor.fetchall()

    context = {
        "reservasi": reservasi,
        "wahana_list": wahana_list,
    }
    return render(request, 'edit_reservasi.html', context)



@login_required_custom
@allowed_roles(['pengunjung','pengunjung_adopter'])
def update_reservasi(request):
    try:
        if request.method == "POST":
            username = request.session.get("username")
            old_fasilitas = request.POST.get("old_fasilitas", "").strip()
            old_tanggal = request.POST.get("old_tanggal", "").strip()
            new_fasilitas = request.POST.get("nama_fasilitas", "").strip()
            new_tanggal = parse_date(request.POST.get("tanggal_kunjungan", ""))
            new_jumlah = request.POST.get("jumlah_tiket", "")

            if not (old_fasilitas and old_tanggal and new_fasilitas and new_tanggal and new_jumlah):
                return redirect('manajemen_atraksi:list_reservasi_pengunjung')

            new_jumlah = int(new_jumlah)

            with connection.cursor() as cursor:
                # Simpan dulu reservasi baru ke tabel temporer (bisa juga dummy insert rollback)
                try:
                    cursor.execute("""
                        INSERT INTO RESERVASI (username_p, nama_fasilitas, tanggal_kunjungan, jumlah_tiket, status)
                        VALUES (%s, %s, %s, %s, 'Pending')
                    """, [username, new_fasilitas, new_tanggal, new_jumlah])
                except DatabaseError as e:
                    msg = str(e).splitlines()[0]
                    encoded_msg = quote(msg)
                    return redirect(f'/show_message/?msg={encoded_msg}&type=error&next_url=manajemen_atraksi:list_reservasi_pengunjung')

                # Kalau berhasil insert → hapus yang lama
                cursor.execute("""
                    DELETE FROM RESERVASI
                    WHERE username_p = %s AND nama_fasilitas = %s AND tanggal_kunjungan = %s
                """, [username, old_fasilitas, old_tanggal])

            return redirect('manajemen_atraksi:list_reservasi_pengunjung')

    except Exception as e:
        msg = str(e).splitlines()[0]
        encoded_msg = quote(msg)
        return redirect(f'/show_message/?msg={encoded_msg}&type=error&next_url=manajemen_atraksi:list_reservasi_pengunjung')

@login_required_custom
@allowed_roles(['pengunjung','pengunjung_adopter'])
def konfirmasi_batal(request, nama_fasilitas, tanggal):
    username = request.session.get("username")
    tanggal_parsed = parse_date(tanggal)

    return render(request, "konfirmasi_batal.html", {
        "nama_fasilitas": nama_fasilitas,
        "tanggal": tanggal,
    })
    
@login_required_custom
@allowed_roles(['pengunjung','pengunjung_adopter'])
def batalkan_reservasi(request, nama_fasilitas, tanggal):
    if request.method == "POST":
        username = request.session.get("username")
        tanggal_parsed = parse_date(tanggal)

        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE RESERVASI
                SET status = 'Dibatalkan'
                WHERE username_p = %s AND nama_fasilitas = %s AND tanggal_kunjungan = %s
            """, [username, nama_fasilitas, tanggal_parsed])

        return redirect('/show_message/?msg=Reservasi berhasil dibatalkan&type=success&next_url=manajemen_atraksi:list_reservasi_pengunjung')
    return redirect('/show_message/?msg=Metode tidak valid&type=error&next_url=manajemen_atraksi:list_reservasi_pengunjung')

@login_required_custom
@allowed_roles(['pengunjung','pengunjung_adopter'])
def form_reservasi(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT nama, jadwal, kapasitas_max
            FROM FASILITAS
            WHERE nama IN (SELECT nama_atraksi FROM ATRAKSI)
        """)
        atraksi = cursor.fetchall()

    context = {
        "atraksi": atraksi
    }
    return render(request, 'form_reservasi.html', context)

from django.db import DatabaseError
from django.shortcuts import redirect
from main.views import show_message  # Import fungsi show_message
from urllib.parse import quote
@login_required_custom
@allowed_roles(['pengunjung','pengunjung_adopter'])
def simpan_reservasi(request):
    if request.method == "POST":
        try:
            username = request.session.get("username")
            nama_fasilitas = request.POST.get("nama_fasilitas")
            tanggal_raw = request.POST.get("tanggal_kunjungan")
            print("📅 Raw tanggal dari POST:", tanggal_raw)
            tanggal_str = request.POST.get("tanggal_kunjungan")
            tanggal = datetime.strptime(tanggal_str, "%Y-%m-%d").date()            
            jumlah = int(request.POST.get("jumlah_tiket"))
            print("📥 POST DATA:")
            print("nama_fasilitas:", nama_fasilitas)
            print("tanggal_kunjungan:", tanggal)
            print("jumlah_tiket:", jumlah)

            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO RESERVASI (username_p, nama_fasilitas, tanggal_kunjungan, jumlah_tiket, status)
                    VALUES (%s, %s, %s, %s, 'Terjadwal')
                """, [username, nama_fasilitas, tanggal, jumlah])

            # Pesan sukses
            return redirect(f'/show_message/?msg=Reservasi berhasil disimpan&type=success&next_url=manajemen_atraksi:list_reservasi_pengunjung')

        except DatabaseError as e:
            # Ambil pesan ERROR dari exception PostgreSQL
            msg = str(e).splitlines()[0]  # Ambil baris pertama
            encoded_msg = quote(msg)  # Encode pesan error untuk URL
            return redirect(f'/show_message/?msg={encoded_msg}&type=error&next_url=manajemen_atraksi:list_reservasi_pengunjung')

    

@login_required_custom
@allowed_roles(['staf admin'])
def list_semua_reservasi(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT r.username_p, r.nama_fasilitas, f.jadwal, r.tanggal_kunjungan, 
                   r.jumlah_tiket, r.status
            FROM RESERVASI r
            JOIN FASILITAS f ON r.nama_fasilitas = f.nama
            ORDER BY r.tanggal_kunjungan DESC
        """)
        semua_reservasi = cursor.fetchall()

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                w.nama_wahana AS nama,
                f.jadwal,
                f.kapasitas_max AS kapasitas,
                w.peraturan
            FROM wahana w
            JOIN fasilitas f ON w.nama_wahana = f.nama
        """)
        wahana_list = cursor.fetchall()

    # Split peraturan by koma
    for i in range(len(wahana_list)):
        wahana = dict(
            nama=wahana_list[i][0],
            jadwal=wahana_list[i][1],
            kapasitas=wahana_list[i][2],
            peraturan=wahana_list[i][3].split(",") if wahana_list[i][3] else []
        )
        wahana_list[i] = wahana

    context = {
        "semua_reservasi": semua_reservasi,
        "wahana_list": wahana_list,
    }
    return render(request, 'list_reservasi.html', context)

@login_required_custom
@allowed_roles(['staf admin'])
def edit_status_reservasi(request, nama_fasilitas, tanggal):
    if request.method == 'POST':
        status_baru = request.POST.get('status')
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE RESERVASI 
                SET status = %s
                WHERE nama_fasilitas = %s AND tanggal_kunjungan = %s
            """, [status_baru, nama_fasilitas, tanggal])
        return redirect('manajemen_atraksi:list_semua_reservasi')

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT r.username_p, r.nama_fasilitas, r.tanggal_kunjungan, r.status
            FROM RESERVASI r
            WHERE r.nama_fasilitas = %s AND r.tanggal_kunjungan = %s
        """, [nama_fasilitas, tanggal])
        data = cursor.fetchone()

    if not data:
        return redirect('manajemen_atraksi:list_semua_reservasi')

    context = {
        "reservasi": {
            "username": data[0],
            "fasilitas": data[1],
            "tanggal": data[2],
            "status": data[3],
        }
    }
    return render(request, 'edit_status_reservasi.html', context)

from datetime import datetime

# @login_required_custom
# def create_reservasi(request):
#     if request.method == "POST":
#         username = request.session.get("username")
#         nama_fasilitas = request.POST.get("nama_fasilitas")
#         tanggal_str = request.POST.get("tanggal_kunjungan")
#         jumlah_tiket = request.POST.get("jumlah_tiket")
#         print("📥 POST DATA:")
#         print("nama_fasilitas:", nama_fasilitas)
#         print("tanggal_kunjungan:", tanggal_str)
#         print("jumlah_tiket:", jumlah_tiket)

#         if not nama_fasilitas or not tanggal_str or not jumlah_tiket:
#             return redirect('/show_message/?msg=Data tidak lengkap&type=warning&next_url=manajemen_atraksi:list_reservasi_pengunjung')

#         try:
#             # Gunakan datetime.strptime agar dapat mendeteksi error format
#             tanggal = datetime.strptime(tanggal_str, "%Y-%m-%d").date()
#             jumlah = int(jumlah_tiket)

#             with connection.cursor() as cursor:
#                 cursor.execute("""
#                     INSERT INTO RESERVASI (username_p, nama_fasilitas, tanggal_kunjungan, jumlah_tiket, status)
#                     VALUES (%s, %s, %s, %s, 'Terjadwal')
#                 """, [username, nama_fasilitas, tanggal, jumlah])

#             return redirect('/show_message/?msg=Reservasi berhasil dibuat&type=success&next_url=manajemen_atraksi:list_reservasi_pengunjung')

#         except ValueError:
#             return redirect('/show_message/?msg=Format tanggal tidak valid&type=warning&next_url=manajemen_atraksi:form_reservasi')
#         except DatabaseError as e:
#             msg = str(e).splitlines()[0]
#             return redirect(f'/show_message/?msg={quote(msg)}&type=error&next_url=manajemen_atraksi:form_reservasi')

#     return redirect('manajemen_atraksi:form_reservasi')
