from django.shortcuts import render, redirect
from django.db import connection
from main.views import login_required_custom, allowed_roles, get_user_role
from urllib.parse import quote
from uuid import UUID

# ================================
# FITUR: Rekam Medis Hewan
# ================================
@login_required_custom
@allowed_roles(["dokter hewan"])
def view_rekam_medis(request):
    current_username = request.session.get("username")
    role = get_user_role(current_username)
    
    hewan_list = []
    try:
        with connection.cursor() as cursor:
            # Query untuk mendapatkan daftar hewan (id dan nama)
            # Menggunakan "hewan" (huruf kecil, diapit quotes)
            cursor.execute('SELECT id, nama FROM "hewan" ORDER BY nama;')
            hewan_rows = cursor.fetchall()
            for h_row in hewan_rows:
                hewan_list.append({"id": h_row[0], "nama": h_row[1]})
    except Exception as e:
        print(f"Error fetching hewan list: {e}")
        # Tangani error jika gagal mendapatkan daftar hewan

    if request.method == "POST":
        id_hewan = request.POST.get("id_hewan")
        username_dh = request.session.get("username")
        tanggal = request.POST.get("tanggal")
        diagnosis = request.POST.get("diagnosis")
        pengobatan = request.POST.get("pengobatan")
        status = request.POST.get("status_kesehatan")
        catatan = request.POST.get("catatan_tindak_lanjut")

        if not id_hewan:
            return redirect("/show_message/?msg=" + quote("ID Hewan harus dipilih.") + "&type=error&next_url=rekam_medis")
        
        try:
            id_hewan_uuid = UUID(id_hewan)
        except ValueError:
            return redirect("/show_message/?msg=" + quote("Format ID Hewan tidak valid.") + "&type=error&next_url=rekam_medis")

        try:
            with connection.cursor() as cursor:
                # Memanggil stored procedure, nama prosedur tidak berubah
                cursor.callproc("insert_catatan_medis", [
                    id_hewan_uuid, username_dh, tanggal,
                    diagnosis, pengobatan,
                    status, catatan
                ])
            return redirect("/show_message/?msg=" + quote("Catatan medis berhasil ditambahkan") + "&type=success&next_url=rekam_medis")
        except Exception as e:
            error_message = str(e)
            if "invalid input syntax" in error_message:
                error_message = "Format input tidak valid. Mohon periksa kembali data Anda."
            elif "foreign key constraint" in error_message.lower():
                error_message = "ID Hewan tidak valid atau tidak ditemukan. Periksa kembali."
            elif "function insert_catatan_medis" in error_message.lower() and "does not exist" in error_message.lower():
                error_message = "Kesalahan database: Fungsi 'insert_catatan_medis' tidak ditemukan dengan jumlah parameter yang sesuai. Pastikan definisi fungsi di database sudah benar."
            print(f"Error adding rekam medis: {error_message}") # Tambahkan print untuk debugging
            return redirect("/show_message/?msg=" + quote(error_message) + "&type=error&next_url=rekam_medis")
    else: # GET request, untuk menampilkan halaman
        data_rekam_medis = []
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT
                        cm.id_hewan,
                        cm.tanggal_pemeriksaan,
                        dh.nama_depan || ' ' || dh.nama_belakang AS nama_dokter, -- Ambil nama dari PENGGUNA
                        cm.status_kesehatan,
                        cm.diagnosis,
                        cm.pengobatan,
                        cm.catatan_tindak_lanjut
                    FROM
                        "catatan_medis" cm -- Ganti CATATAN_MEDIS jadi "catatan_medis"
                    JOIN
                        "dokter_hewan" d_dh ON cm.username_dh = d_dh.username_dh -- Join ke tabel dokter_hewan
                    JOIN
                        "pengguna" dh ON d_dh.username_dh = dh.username -- Join ke tabel pengguna untuk nama dokter
                    ORDER BY
                        cm.tanggal_pemeriksaan DESC;
                """)
                rows = cursor.fetchall()
                for row in rows:
                    data_rekam_medis.append({
                        'id_hewan': row[0],
                        'tanggal_pemeriksaan': row[1],
                        'nama_dokter': row[2],
                        'status_kesehatan': row[3],
                        'diagnosis': row[4],
                        'pengobatan': row[5],
                        'catatan_tindak_lanjut': row[6],
                    })
        except Exception as e:
            print(f"Error fetching rekam medis: {e}")
            
    return render(request, "rekam_medis.html", {
        "role": role,
        "data_rekam_medis": data_rekam_medis,
        "hewan_list": hewan_list,
        "current_id_hewan": None,
    })

# ================================
# FITUR: Update Rekam Medis
# ================================
@login_required_custom
@allowed_roles(["dokter hewan"])
def update_rekam_medis(request):
    if request.method == "POST":
        id_hewan_original = request.POST.get("id_hewan_original")
        tanggal_original = request.POST.get("tanggal_original")
        
        diagnosis = request.POST.get("diagnosis")
        pengobatan = request.POST.get("pengobatan")
        status_kesehatan = request.POST.get("status_kesehatan")
        catatan_tindak_lanjut = request.POST.get("catatan_tindak_lanjut")

        if not id_hewan_original or not tanggal_original:
            return redirect("/show_message/?msg=" + quote("ID Hewan dan Tanggal Rekam Medis tidak ditemukan untuk update.") + "&type=error&next_url=rekam_medis")

        try:
            id_hewan_uuid = UUID(id_hewan_original)
        except ValueError:
            return redirect("/show_message/?msg=" + quote("Format ID Hewan untuk update tidak valid.") + "&type=error&next_url=rekam_medis")

        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE "catatan_medis" -- Ganti CATATAN_MEDIS jadi "catatan_medis"
                    SET
                        diagnosis = %s,
                        pengobatan = %s,
                        status_kesehatan = %s,
                        catatan_tindak_lanjut = %s
                    WHERE
                        id_hewan = %s AND tanggal_pemeriksaan = %s;
                """, [diagnosis, pengobatan, status_kesehatan, catatan_tindak_lanjut, id_hewan_uuid, tanggal_original])
            
            return redirect("/show_message/?msg=" + quote("Rekam medis berhasil diperbarui.") + "&type=success&next_url=rekam_medis")
        except Exception as e:
            error_message = str(e)
            if "invalid input syntax" in error_message:
                error_message = "Format input tidak valid. Mohon periksa kembali data Anda."
            print(f"Error updating rekam medis: {error_message}") # Tambahkan print
            return redirect("/show_message/?msg=" + quote(f"Error memperbarui rekam medis: {error_message}") + "&type=error&next_url=rekam_medis")
    
    return redirect("rekam_medis")

# ================================
# FITUR: Delete Rekam Medis
# ================================
@login_required_custom
@allowed_roles(["dokter hewan"])
def delete_rekam_medis(request):
    if request.method == "GET":
        id_hewan = request.GET.get("id_hewan")
        tanggal = request.GET.get("tanggal")

        if not id_hewan or not tanggal:
            return redirect("/show_message/?msg=" + quote("ID Hewan atau Tanggal Rekam Medis tidak ditemukan untuk dihapus.") + "&type=error&next_url=rekam_medis")

        try:
            id_hewan_uuid = UUID(id_hewan)
        except ValueError:
            return redirect("/show_message/?msg=" + quote("Format ID Hewan untuk delete tidak valid.") + "&type=error&next_url=rekam_medis")

        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM "catatan_medis" -- Ganti CATATAN_MEDIS jadi "catatan_medis"
                    WHERE id_hewan = %s AND tanggal_pemeriksaan = %s;
                """, [id_hewan_uuid, tanggal])
            
            return redirect("/show_message/?msg=" + quote("Rekam medis berhasil dihapus.") + "&type=success&next_url=rekam_medis")
        except Exception as e:
            error_message = str(e)
            if "invalid input syntax" in error_message:
                error_message = "Format input tidak valid. Mohon periksa kembali data Anda."
            print(f"Error deleting rekam medis: {error_message}") # Tambahkan print
            return redirect("/show_message/?msg=" + quote(f"Error menghapus rekam medis: {error_message}") + "&type=error&next_url=rekam_medis")
    
    return redirect("rekam_medis")

# ================================
# FITUR: Jadwal Pemeriksaan Kesehatan
# ================================
@login_required_custom
@allowed_roles(["dokter hewan"])
def view_jadwal_pemeriksaan(request):
    current_username = request.session.get("username")
    role = get_user_role(current_username)

    hewan_list = []
    try:
        with connection.cursor() as cursor:
            # Menggunakan "hewan" (huruf kecil, diapit quotes)
            cursor.execute('SELECT id, nama FROM "hewan" ORDER BY nama;')
            hewan_rows = cursor.fetchall()
            for h_row in hewan_rows:
                hewan_list.append({"id": h_row[0], "nama": h_row[1]})
    except Exception as e:
        print(f"Error fetching hewan list for jadwal: {e}")

    if request.method == "POST":
        id_hewan = request.POST.get("id_hewan")
        tanggal_awal = request.POST.get("tanggal_awal")
        frekuensi = int(request.POST.get("frekuensi"))

        try:
            id_hewan_uuid = UUID(id_hewan)
        except ValueError:
            return redirect("/show_message/?msg=" + quote("Format ID Hewan untuk jadwal tidak valid.") + "&type=error&next_url=jadwal_pemeriksaan")

        try:
            with connection.cursor() as cursor:
                # Nama prosedur tidak berubah
                cursor.callproc("tambah_jadwal_rutin", [
                    id_hewan_uuid, tanggal_awal, frekuensi
                ])
            return redirect("/show_message/?msg=" + quote("Jadwal pemeriksaan berhasil ditambahkan.") + "&type=success&next_url=jadwal_pemeriksaan")
        except Exception as e:
            error_message = str(e)
            if "invalid input syntax" in error_message:
                error_message = "Format input tidak valid. Mohon periksa kembali data Anda."
            elif "foreign key constraint" in error_message.lower():
                 error_message = "ID Hewan tidak valid. Pastikan Anda memasukkan ID hewan yang sudah ada."
            print(f"Error adding jadwal: {error_message}") # Tambahkan print
            return redirect("/show_message/?msg=" + quote(error_message) + "&type=error&next_url=jadwal_pemeriksaan")
    else: # GET request, untuk menampilkan halaman dengan data
        data_jadwal = []
        frekuensi_rutin_display = "N/A"

        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT
                        jpk.id_hewan,
                        h.nama AS nama_hewan,
                        jpk.tgl_pemeriksaan_selanjutnya,
                        jpk.freq_pemeriksaan_rutin
                    FROM
                        "jadwal_pemeriksaan_kesehatan" jpk -- Ganti JADWAL_PEMERIKSAAN_KESEHATAN jadi "jadwal_pemeriksaan_kesehatan"
                    JOIN
                        "hewan" h ON jpk.id_hewan = h.id -- Ganti HEWAN jadi "hewan"
                    ORDER BY
                        h.nama, jpk.tgl_pemeriksaan_selanjutnya;
                """)
                rows = cursor.fetchall()
                for row in rows:
                    data_jadwal.append({
                        'id_hewan': row[0],
                        'nama_hewan': row[1],
                        'tgl_pemeriksaan_selanjutnya': row[2],
                        'freq_pemeriksaan_rutin': row[3],
                    })
            
            if data_jadwal and data_jadwal[0]['freq_pemeriksaan_rutin']:
                frekuensi_rutin_display = f"{data_jadwal[0]['freq_pemeriksaan_rutin']} bulan sekali"
            else:
                frekuensi_rutin_display = "Belum Diatur"

        except Exception as e:
            print(f"Error fetching jadwal pemeriksaan: {e}")
            
        return render(request, "jadwal_pemeriksaan_kesehatan.html", {
            "role": role,
            "data_jadwal": data_jadwal,
            "frekuensi_rutin_display": frekuensi_rutin_display,
            "hewan_list": hewan_list,
        })

# ================================
# FITUR: Update Jadwal Pemeriksaan
# ================================
@login_required_custom
@allowed_roles(["dokter hewan"])
def update_jadwal_pemeriksaan(request):
    if request.method == "POST":
        id_hewan_original = request.POST.get("id_hewan_original")
        tgl_original = request.POST.get("tgl_original")
        new_frekuensi = request.POST.get("frekuensi")

        if not id_hewan_original or not tgl_original or not new_frekuensi:
            return redirect("/show_message/?msg=" + quote("Data tidak lengkap untuk memperbarui jadwal.") + "&type=error&next_url=jadwal_pemeriksaan")
        
        try:
            new_frekuensi = int(new_frekuensi)
            id_hewan_uuid = UUID(id_hewan_original)
        except ValueError:
            return redirect("/show_message/?msg=" + quote("Format ID Hewan untuk update jadwal tidak valid.") + "&type=error&next_url=jadwal_pemeriksaan")

        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE "jadwal_pemeriksaan_kesehatan" -- Ganti JADWAL_PEMERIKSAAN_KESEHATAN jadi "jadwal_pemeriksaan_kesehatan"
                    SET freq_pemeriksaan_rutin = %s
                    WHERE id_hewan = %s AND tgl_pemeriksaan_selanjutnya = %s;
                """, [new_frekuensi, id_hewan_uuid, tgl_original])
            
            return redirect("/show_message/?msg=" + quote("Frekuensi jadwal pemeriksaan berhasil diperbarui.") + "&type=success&next_url=jadwal_pemeriksaan")
        except ValueError:
            return redirect("/show_message/?msg=" + quote("Frekuensi harus berupa angka.") + "&type=error&next_url=jadwal_pemeriksaan")
        except Exception as e:
            error_message = str(e)
            if "invalid input syntax" in error_message:
                error_message = "Format input tidak valid. Mohon periksa kembali data Anda."
            print(f"Error updating jadwal: {error_message}") # Tambahkan print
            return redirect("/show_message/?msg=" + quote(f"Error memperbarui jadwal: {error_message}") + "&type=error&next_url=jadwal_pemeriksaan")
    
    return redirect("jadwal_pemeriksaan")

# ================================
# FITUR: Delete Jadwal Pemeriksaan
# ================================
@login_required_custom
@allowed_roles(["dokter hewan"])
def delete_jadwal_pemeriksaan(request):
    if request.method == "GET":
        id_hewan = request.GET.get("id_hewan")
        tanggal = request.GET.get("tanggal")

        if not id_hewan or not tanggal:
            return redirect("/show_message/?msg=" + quote("Data tidak lengkap untuk menghapus jadwal.") + "&type=error&next_url=jadwal_pemeriksaan")

        try:
            id_hewan_uuid = UUID(id_hewan)
        except ValueError:
            return redirect("/show_message/?msg=" + quote("Format ID Hewan untuk delete jadwal tidak valid.") + "&type=error&next_url=jadwal_pemeriksaan")

        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM "jadwal_pemeriksaan_kesehatan" -- Ganti JADWAL_PEMERIKSAAN_KESEHATAN jadi "jadwal_pemeriksaan_kesehatan"
                    WHERE id_hewan = %s AND tgl_pemeriksaan_selanjutnya = %s;
                """, [id_hewan_uuid, tanggal])
            
            return redirect("/show_message/?msg=" + quote("Jadwal pemeriksaan berhasil dihapus.") + "&type=success&next_url=jadwal_pemeriksaan")
        except Exception as e:
            error_message = str(e)
            if "invalid input syntax" in error_message:
                error_message = "Format input tidak valid. Mohon periksa kembali data Anda."
            print(f"Error deleting jadwal: {error_message}") # Tambahkan print
            return redirect("/show_message/?msg=" + quote(f"Error menghapus jadwal: {error_message}") + "&type=error&next_url=jadwal_pemeriksaan")
    
    return redirect("jadwal_pemeriksaan")

# Fungsi profile (klo masih perlu si)
def profile(request):
    current_username = request.session.get("username")
    role = get_user_role(current_username)
    context = {
        "role" : role
    }
    return render(request, 'profile.html', context)