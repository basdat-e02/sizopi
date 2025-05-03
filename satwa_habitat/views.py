from shlex import quote
from django.shortcuts import redirect, render
from django.db import connection
from django.urls import reverse
from django.utils.dateparse import parse_date
from main.views import allowed_roles, get_user_role, unauthenticated_user, login_required_custom  

@login_required_custom
@allowed_roles(["dokter hewan","penjaga hewan","staf admin",]) 
def view_satwa(request):
    try:
        if request.method == 'POST' and request.POST.get('_method') == 'DELETE':
            id_to_delete = request.POST.get('id')
            if id_to_delete:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT delete_hewan(%s)", [str(id_to_delete)])
    except Exception as e:
        return redirect(f'/show_message/?msg={str(e)}&type=error')

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM get_all_hewan()")
        hewans = cursor.fetchall()

    satwa_list = []
    for hewan in hewans:
        satwa_list.append({
            'id' : hewan[0],
            'nama' : hewan[1],
            'spesies' : hewan[2],
            'asal' : hewan[3],
            'tanggal_lahir' : hewan[4],
            'status' : hewan[5],
            'habitat' : hewan[6],
        })

    context = {
        "role": get_user_role(request.session.get('username')),
        "satwa_list": satwa_list,
    }

    return render(request, 'view_satwa.html', context)

@login_required_custom
@allowed_roles(["dokter hewan","penjaga hewan","staf admin",])
def create_satwa(request):
    try:
        if request.method == 'POST':
            nama = request.POST.get('nama') or None
            spesies = request.POST.get('spesies')
            asal = request.POST.get('asal')
            tanggal_lahir = request.POST.get('tanggal_lahir') or None
            status_kesehatan = request.POST.get('status_kesehatan')
            habitat = request.POST.get('habitat')
            foto = request.POST.get('foto') or None

            if tanggal_lahir == '':
                tanggal_lahir = None
            else:
                tanggal_lahir = parse_date(tanggal_lahir)

            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT insert_hewan(%s, %s, %s, %s, %s, %s, %s)",
                    [nama, spesies, asal, tanggal_lahir, status_kesehatan, habitat, foto]
                )
            
            return redirect('view_satwa')
    except Exception as e:
        return redirect(f'/show_message/?msg={str(e)}&type=error')
    
    nama_habitat_list = []

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM get_all_habitats()")
        habitats = cursor.fetchall()
    
    for habitat in habitats:
        nama_habitat_list.append(habitat[0])

    context = {
        "role": get_user_role(request.session.get('username')),
        'nama_habitat_list': nama_habitat_list,
    }
    return render(request, 'create_satwa.html', context)

@login_required_custom
@allowed_roles(["dokter hewan", "penjaga hewan", "staf admin"])
def edit_satwa(request, uuid):
    try:
        if request.method == 'POST':
            nama           = request.POST.get('nama')
            spesies        = request.POST.get('spesies')
            asal           = request.POST.get('asal')
            tanggal_lahir  = request.POST.get('tanggal_lahir') or None
            status         = request.POST.get('status_kesehatan')
            habitat        = request.POST.get('habitat')
            foto           = request.POST.get('foto')

            with connection.cursor() as cursor:
                pgconn = cursor.connection          # ← psycopg2 connection
                pgconn.notices.clear()              # bersihkan notice lama

                cursor.execute("""
                    SELECT update_hewan(%s,%s,%s,%s,%s,%s,%s,%s)
                """, [
                    uuid, nama, spesies, asal,
                    tanggal_lahir, status, habitat, foto
                ])

                # salin notice sebelum keluar dari blok WITH
                notices = pgconn.notices[:]
                pgconn.notices.clear()

            if notices:
                raw = notices[-1]                                 # ambil yang terakhir
                notice_msg = raw.replace('NOTICE:', '').strip()   # rapikan
            else:
                notice_msg = 'Data satwa berhasil diperbarui.'

            return redirect(f'/show_message/?msg={quote(notice_msg)}&type=success&next_url=view_satwa')

    except Exception as e:
        return redirect(f'/show_message/?msg={quote(str(e))}&type=error')

    nama_habitat_list = []

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM get_all_habitats()")
        habitats = cursor.fetchall()
    
    for habitat in habitats:
        nama_habitat_list.append(habitat[0])

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM get_hewan_by_id(%s)", [uuid])
        hewan = cursor.fetchone()
    
    hewan = {
        'id' : hewan[0],
        'nama' : hewan[1],
        'spesies' : hewan[2],
        'asal' : hewan[3],
        "tanggal_lahir" : hewan[4].strftime('%Y-%m-%d') if hewan[4] else '',
        'status' : hewan[5],
        'habitat' : hewan[6],
        'foto' : hewan[7],
    }

    context = {
        "role": get_user_role(request.session.get('username')),
        'satwa' : hewan,
        'nama_habitat_list' : nama_habitat_list,
    }
    return render(request, 'edit_satwa.html', context)

@login_required_custom
@allowed_roles(["penjaga hewan","staf admin",])
def view_habitat(request):
    try:
        if request.method == 'POST' and request.POST.get('_method') == 'DELETE':
            nama_to_delete = request.POST.get('nama')
            if nama_to_delete:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT delete_habitat(%s)", [str(nama_to_delete)])
    except Exception as e:
        return redirect(f'/show_message/?msg={str(e)}&type=error')
    
    habitat_list = []

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM get_all_habitats()")
        habitats = cursor.fetchall()
    
    for habitat in habitats:
        habitat_list.append(
            {
                "nama" : habitat[0],
                "luas" : habitat[1],
                "kapasitas" : habitat[2],
                "status" : habitat[3]
            }
        )

    context = {
        "role": get_user_role(request.session.get('username')),
        "habitat_list": habitat_list
    }
    return render(request, 'view_habitat.html', context)

@login_required_custom
@allowed_roles(["penjaga hewan","staf admin",])
def detail_habitat(request, nama):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM get_habitat_by_name(%s)", [nama])
        habitat = cursor.fetchone()
    
    habitat= {
        "nama": habitat[0],
        "luas": float(habitat[1]),
        "kapasitas": habitat[2],
        "status": habitat[3]
    }

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM get_hewan_by_habitat(%s)", [nama])
        hewans = cursor.fetchall()
    
    hewan_list = []
    for hewan in hewans:
        hewan_list.append({
            'id' : hewan[0],
            'nama' : hewan[1],
            'spesies' : hewan[2],
            'asal' : hewan[3],
            "tanggal_lahir" : hewan[4],
            'status' : hewan[5],
            'habitat' : hewan[6],
        })


    context = {
        "role": get_user_role(request.session.get('username')),
        "habitat": habitat,
        "hewan_list": hewan_list
    }
    return render(request, 'detail_habitat.html', context)

@login_required_custom
@allowed_roles(["penjaga hewan","staf admin",])
def create_habitat(request):
    try :
        if request.method == 'POST':
            nama = request.POST.get('nama')
            luas_area = request.POST.get('luas_area')
            kapasitas = request.POST.get('kapasitas')
            status = request.POST.get('status')

            with connection.cursor() as cursor:
                cursor.execute("SELECT insert_habitat(%s, %s, %s, %s)", [nama, luas_area, kapasitas, status])

            return redirect('view_habitat')
    except Exception as e:
        return redirect(f'/show_message/?msg={str(e)}&type=error')

    context = {"role": get_user_role(request.session.get('username'))}
    return render(request, 'create_habitat.html', context)

@login_required_custom
@allowed_roles(["penjaga hewan","staf admin",])
def edit_habitat(request, nama):
    try:
        if request.method == 'POST':
            new_nama = request.POST.get('nama')
            luas_area = request.POST.get('luas_area')
            kapasitas = request.POST.get('kapasitas')
            status = request.POST.get('status')

            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT update_habitat(%s, %s, %s, %s)
                """, [new_nama, luas_area, kapasitas, status])
            
            return redirect('view_habitat')
    except Exception as e:
        return redirect(f'/show_message/?msg={str(e)}&type=error')
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM get_habitat_by_name(%s)", [nama])
        habitat = cursor.fetchone()
    
    habitat= {
        "nama": habitat[0],
        "luas": float(habitat[1]),
        "kapasitas": habitat[2],
        "status": habitat[3]
    }

    context = {
        "role": get_user_role(request.session.get('username')),
        "habitat": habitat,
    }
    return render(request, 'edit_habitat.html', context)