from django.shortcuts import render, redirect
from django.db import connection
from main.views import login_required_custom, allowed_roles, get_user_role
from urllib.parse import quote

# def view_pemberian_pakan(request):
#     return render(request, 'pemberian_pakan.html')

# def view_riwayat_pemberian_pakan(request):
#     return render(request, 'riwayat_pemberian_pakan.html')


# ================================
# FITUR: Pemberian Pakan
# ================================
@login_required_custom
@allowed_roles(["penjaga hewan"])
def view_pemberian_pakan(request):
    if request.method == "POST":
        id_hewan = request.POST.get("id_hewan")
        jadwal = request.POST.get("jadwal")
        jenis = request.POST.get("jenis")
        jumlah = request.POST.get("jumlah")
        status = request.POST.get("status")
        username_jh = request.session.get("username")

        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO PAKAN(id_hewan, jadwal, jenis, jumlah, status)
                    VALUES (%s, %s, %s, %s, %s)
                """, [id_hewan, jadwal, jenis, jumlah, status])

                cursor.execute("""
                    INSERT INTO MEMBERI(id_hewan, jadwal, username_jh)
                    VALUES (%s, %s, %s)
                """, [id_hewan, jadwal, username_jh])

            return redirect("/show_message/?msg=" + quote("Pemberian pakan berhasil dicatat.") + "&type=success&next_url=pemberian_pakan")
        except Exception as e:
            return redirect("/show_message/?msg=" + quote(str(e)) + "&type=error")

    return render(request, "pemberian_pakan.html", {"role": get_user_role(request.session.get("username"))})


# ================================
# FITUR: Riwayat Pemberian Pakan
# ================================
@login_required_custom
@allowed_roles(["penjaga hewan"])
def view_riwayat_pemberian_pakan(request):
    riwayat = []
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM RIWAYAT_PAKAN ORDER BY waktu_aksi DESC")
            hasil = cursor.fetchall()

            for row in hasil:
                riwayat.append({
                    "id": row[0],
                    "id_hewan": row[1],
                    "jadwal": row[2],
                    "jenis": row[3],
                    "jumlah": row[4],
                    "status_lama": row[5],
                    "status_baru": row[6],
                    "waktu_aksi": row[7],
                })
    except Exception as e:
        return redirect("/show_message/?msg=" + quote(str(e)) + "&type=error")

    return render(request, "riwayat_pemberian_pakan.html", {
        "role": get_user_role(request.session.get("username")),
        "riwayat": riwayat
    })
