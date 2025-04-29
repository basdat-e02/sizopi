from django.shortcuts import render, redirect
from django.db import transaction
from django.db import connection

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
    query = "SELECT nama FROM HEWAN;"
    return execute_query(query, fetch=True)
def get_pelatih_choices():
    with connection.cursor() as cursor:
        cursor.execute("SELECT username, nama_depan, nama_belakang FROM PELATIH_HEWAN")
        result = cursor.fetchall()
    return [(row[0], f'{row[1]} {row[2]}') for row in result]  # Menggabungkan nama depan dan belakang

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
def atraksi_list(request):
    query = """
    SELECT 
        a.nama_atraksi AS nama,
        a.lokasi,
        f.jadwal,
        f.kapasitas_max AS kapasitas,
        STRING_AGG(DISTINCT p.nama_depan || ' ' || COALESCE(p.nama_tengah || ' ', '') || p.nama_belakang, ', ') AS pelatih,
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
        "role": "staf admin"
    })

@transaction.atomic
def atraksi_create(request):
    if request.method == 'POST':
        try:
            # Ambil nilai dari form POST
            nama = request.POST.get('nama')
            jadwal = request.POST.get('jadwal')
            kapasitas = request.POST.get('kapasitas')
            lokasi = request.POST.get('lokasi')
            pelatih = request.POST.get('pelatih')
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
            
            # 3. Insert jadwal penugasan pelatih (jika ada pelatih)
            if pelatih:
                query_penugasan = """
                INSERT INTO jadwal_penugasan (username_lh, tgl_penugasan, nama_atraksi)
                VALUES (%s, NOW(), %s)
                """
                execute_query(query_penugasan, [pelatih, nama])
            
            # 4. Insert hewan yang berpartisipasi (jika ada hewan)
            for hewan_id in hewan_ids:
                query_berpartisipasi = """
                INSERT INTO berpartisipasi (nama_fasilitas, id_hewan)
                VALUES (%s, %s)
                """
                execute_query(query_berpartisipasi, [nama, hewan_id])
            
            # Jika semua query berhasil, redirect ke daftar atraksi
            return redirect('manajemen_atraksi:atraksi_list')
            
        except Exception as e:
            # Tangkap error dan tampilkan ke pengguna
            return render(request, 'atraksi_form.html', {
                "error": str(e),
                "action": "Tambah",
                "pelatih_list": get_pelatih_list(),
                "hewan_list": get_hewan_list(),
                "role": "staf admin"
            })
    
    # Jika bukan POST, tampilkan halaman form untuk tambah atraksi
    return render(request, 'atraksi_form.html', {
        "action": "Tambah",
        "pelatih_list": get_pelatih_list(),
        "hewan_list": get_hewan_list(),
        "role": "staf admin"
    })

@transaction.atomic
def atraksi_update(request, nama):
    if request.method == 'POST':
        lokasi = request.POST.get('lokasi')
        kapasitas = request.POST.get('kapasitas')
        jadwal = request.POST.get('jadwal')
        pelatih = request.POST.get('pelatih')
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
                execute_query(
                    "INSERT INTO jadwal_penugasan (username_lh, tgl_penugasan, nama_atraksi) VALUES (%s, NOW(), %s)",
                    [pelatih, nama]
                )
            
            # 4. Update hewan
            execute_query(
                "DELETE FROM berpartisipasi WHERE nama_fasilitas = %s", 
                [nama]
            )
            for hewan_id in hewan_ids:
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
                "role": "staf admin"
            })
    
    atraksi = get_atraksi_by_nama(nama)
    atraksi['hewan_terlibat'] = get_hewan_by_atraksi(nama)
    
    return render(request, 'atraksi_form.html', {
        "atraksi": atraksi,
        "action": "Edit",
        "pelatih_list": get_pelatih_list(),
        "hewan_list": get_hewan_list(),
        "role": "staf admin"
    })


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
                "role": "staf admin"
            })

    # Jika bukan POST, tampilkan halaman konfirmasi penghapusan
    atraksi = get_atraksi_by_nama(nama)
    return render(request, 'atraksi_confirm_delete.html', {
        "atraksi": atraksi,
        "role": "staf admin"
    })




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
        "role": "staf admin"
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
                "role": "staf admin"
            })
    
    return render(request, 'wahana_form.html', {
        "action": "Tambah",
        "role": "staf admin"
    })

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
                "role": "staf admin"
            })
    
    wahana = get_wahana_by_nama(nama)
    return render(request, 'wahana_form.html', {
        "wahana": wahana,
        "action": "Edit",
        "role": "staf admin"
    })

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
                "role": "staf admin"
            })
    
    wahana = get_wahana_by_nama(nama)
    return render(request, 'wahana_confirm_delete.html', {
        "wahana": wahana,
        "role": "staf admin"
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


from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection

def execute_query(query, params=None, fetch=False):
    with connection.cursor() as cursor:
        cursor.execute(query, params or [])
        if fetch:
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        return cursor.rowcount

def reservasi_list(request, role):
    # Dummy data untuk testing
    reservasi = [
        {
            'nama_pengunjung' : 'Agus',
            'nama_fasilitas': 'Roller Coaster',
            'tanggal_kunjungan': '2025-05-01',
            'jumlah_tiket': 2,
            'status': 'Terjadwal',
        },
        {
            'nama_pengunjung' : 'Budi',
            'nama_fasilitas': 'Rumah Hantu',
            'tanggal_kunjungan': '2025-05-03',
            'jumlah_tiket': 4,
            'status': 'Terjadwal',
        },
    ]
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

    # Tampilkan nama role dengan format yang diinginkan
    role_display = {
        'staf': 'staf admin',
        'pengunjung': 'pengunjung'
    }.get(role, role)

    return render(request, f'reservasi_{role}_list.html', {
        'reservasi': reservasi,
        'action': f'Daftar Reservasi - {role_display.capitalize()}',
        'role': role_display,
        "wahana_list": wahana_list,

    })


# Reservasi Create
# views.py
def reservasi_create(request):
    if request.method == 'POST':
        # Ambil data dari form
        nama_atraksi = request.POST.get('nama_atraksi')
        tanggal = request.POST.get('tanggal')
        jumlah_tiket = int(request.POST.get('jumlah_tiket', 0))

        # Lakukan logika lainnya untuk membuat reservasi
        # Misalnya, simpan data reservasi ke database atau model lain
        
        # Contoh simulasi penyimpanan reservasi
        # Reservasi.objects.create(nama_atraksi=nama_atraksi, tanggal=tanggal, jumlah_tiket=jumlah_tiket)

        # Kirim pesan sukses setelah reservasi berhasil dibuat
        messages.success(request, "Reservasi berhasil dibuat!")
        return redirect('reservasi_list', role='pengunjung')  # Pastikan role atau URL sudah sesuai

    # Jika method GET, ambil daftar atraksi untuk dropdown
    atraksi = [
        {'nama_atraksi': 'Roller Coaster'},
        {'nama_atraksi': 'Rumah Hantu'}
    ]

    # Render halaman reservasi dengan data atraksi dan role
    return render(request, 'reservasi_create_list.html', {'atraksi': atraksi, 'role': 'pengunjung'})




def reservasi_edit(request, nama_atraksi, tanggal):
    # Dummy data untuk update (seharusnya ambil dari database)
    reservasi = {
        'nama_fasilitas': nama_atraksi,
        'tanggal_kunjungan': tanggal,
        'jumlah_tiket': 2,
        'status': 'Terjadwal',
    }

    if request.method == 'POST':
        new_tanggal = request.POST.get('tanggal')
        new_jumlah_tiket = int(request.POST.get('jumlah_tiket'))

        # Simulasi update database (misalnya dengan ORM atau query lainnya)
        reservasi['tanggal_kunjungan'] = new_tanggal
        reservasi['jumlah_tiket'] = new_jumlah_tiket

        # Pesan sukses
        messages.success(request, "Reservasi berhasil diperbarui!")
        return redirect('reservasi_list', role=request.GET.get('role', 'pengunjung'))  # Redirect berdasarkan role

    return render(request, 'reservasi_form.html', {
        'reservasi': reservasi,
        'action': 'Edit Reservasi',
        'role': request.GET.get('role', 'pengunjung'),
    })

def reservasi_delete(request, nama_atraksi, tanggal):
    # Dummy data untuk delete (seharusnya ambil dari database)
    reservasi = {
        'nama_fasilitas': nama_atraksi,
        'tanggal_kunjungan': tanggal,
        'jumlah_tiket': 2,
        'status': 'Terjadwal',
    }

    if request.method == 'POST':
        # Simulasi delete dari database
        # Reservasi akan dihapus di sini (misalnya dengan ORM atau query lainnya)
        messages.success(request, "Reservasi berhasil dibatalkan!")
        return redirect('reservasi_list', role=request.GET.get('role', 'pengunjung'))  # Redirect sesuai role

    return render(request, 'reservasi_confirm_delete.html', {
        'nama_atraksi': nama_atraksi,
        'tanggal': tanggal,
    })
