from shlex import quote
from datetime import date, timedelta
from collections import defaultdict
from datetime import datetime
from django.shortcuts import render, redirect
from django.db import connection
from django.utils import timezone
from django.utils.dateformat import DateFormat

from main.views import login_required_custom, allowed_roles, get_user_role


def dictfetchall(cursor):
    "Helper: hasil fetchall jadi list of dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


# ————————————————————
# 1. Manajemen Adopter
# ————————————————————

@login_required_custom
@allowed_roles(['staf admin'])
def view_adopter(request):
    if request.method == 'POST' and request.POST.get('_method') == 'DELETE':
        id_to_delete = request.POST.get('id')
        try:
            with connection.cursor() as cur:
                cur.execute("SELECT delete_adopter(%s)", [id_to_delete])
        except Exception as e:
            return redirect(f'/show_message/?msg={quote(str(e))}&type=error')

    with connection.cursor() as cur:
        cur.execute("SELECT * FROM get_all_adopters()")
        rows = cur.fetchall()
    adopter_list = [
        {'id': r[0], 'username': r[1], 'tipe': r[2], 'nama': r[3], 'identifier': r[4], 'total': r[5]}
        for r in rows
    ]
    return render(request, 'view_adopter.html', {
        'role': get_user_role(request.session.get('username')),
        'adopter_list': adopter_list
    })


@login_required_custom
@allowed_roles(['staf admin'])
def create_adopter(request):
    if request.method == 'POST':
        jenis    = request.POST.get('jenis')
        username = request.POST.get('username')
        try:
            with connection.cursor() as cur:
                if jenis == 'individu':
                    nik  = request.POST.get('nik')
                    nama = request.POST.get('nama')
                    cur.execute("SELECT insert_adopter_individu(%s, %s, %s)", [username, nik, nama])
                else:
                    npp      = request.POST.get('npp')
                    nama_org = request.POST.get('nama_org')
                    cur.execute("SELECT insert_adopter_organisasi(%s, %s, %s)", [username, npp, nama_org])
        except Exception as e:
            return redirect(f'/show_message/?msg={quote(str(e))}&type=error')
        return redirect('view_adopter')

    return render(request, 'create_adopter.html', {
        'role': get_user_role(request.session.get('username'))
    })


# ————————————————————
# 2. Manajemen Adopsi (Admin)
# ————————————————————

@login_required_custom
@allowed_roles(['staf admin'])
def view_adopsi(request):
    with connection.cursor() as cur:
        cur.execute("""
            SELECT
              h.id                    AS id_hewan,
              h.nama                  AS nama,
              h.spesies               AS jenis,
              h.status_kesehatan      AS kondisi,
              ad.id_adopter           AS id_adopter,
              ad.tgl_mulai_adopsi     AS tgl_mulai_adopsi
            FROM HEWAN h
            LEFT JOIN LATERAL (
              SELECT id_adopter, tgl_mulai_adopsi
              FROM ADOPSI
              WHERE id_hewan = h.id
              ORDER BY tgl_mulai_adopsi DESC
              LIMIT 1
            ) ad ON TRUE
            ORDER BY h.nama;
        """)
        rows = cur.fetchall()

    animals = []
    for id_h, nama, jenis, kondisi, id_adp, tgl_mul in rows:
        animals.append({
            'id_hewan':          id_h,
            'nama':              nama,
            'jenis':             jenis,
            'kondisi':           kondisi,
            'id_adopter':        id_adp,
            'tgl_mulai_adopsi':  DateFormat(tgl_mul).format('Y-m-d') if tgl_mul else None,
        })

    return render(request, 'view_adopsi.html', {
        'role':    get_user_role(request.session.get('username')),
        'animals': animals,
    })
    
@login_required_custom
@allowed_roles(['staf admin'])
def pendataan_adopter(request, id_hewan):
    if request.method == 'POST':
        jenis    = request.POST.get('jenis')
        username = request.POST.get('username')
        try:
            with connection.cursor() as cur:
                # 1) Buat Adopter
                if jenis == 'individu':
                    nik  = request.POST.get('nik')
                    nama = request.POST.get('nama')
                    cur.execute("SELECT insert_adopter_individu(%s, %s, %s)",
                                [username, nik, nama])
                else:
                    npp      = request.POST.get('npp')
                    nama_org = request.POST.get('nama_org')
                    cur.execute("SELECT insert_adopter_organisasi(%s, %s, %s)",
                                [username, npp, nama_org])
                new_adopter_id = cur.fetchone()[0]

                # 2) Buat Adopsi (1 tahun, contrib default 0)
                from datetime import date, timedelta
                tgl_mulai   = date.today()
                tgl_berhenti= tgl_mulai + timedelta(days=365)
                cur.execute(
                  "SELECT insert_adopsi(%s, %s, %s, %s, %s, %s)",
                  [new_adopter_id, id_hewan, tgl_mulai, tgl_berhenti, 0, 'Pending']
                )

            return redirect('view_adopsi')
        except Exception as e:
            error = str(e)
            return render(request, 'pendataan_adopter.html', {
                'role': get_user_role(request.session.get('username')),
                'id_hewan': id_hewan,
                'error': error
            })

    return render(request, 'pendataan_adopter.html', {
        'role':     get_user_role(request.session.get('username')),
        'id_hewan': id_hewan,
        'error':    None
    })

@login_required_custom
@allowed_roles(['staf admin'])
def detail_adopsi(request, id_adopter, id_hewan, tgl_mulai_adopsi):
    # parse the slug into a date object
    mulai_date = datetime.strptime(tgl_mulai_adopsi, '%Y-%m-%d').date()

    # if the status‐update form was submitted
    if request.method == 'POST' and request.POST.get('action') == 'save':
        new_status = request.POST.get('status_pembayaran')
        try:
            with connection.cursor() as cur:
                cur.execute("""
                    UPDATE ADOPSI
                       SET status_pembayaran = %s
                     WHERE id_adopter       = %s
                       AND id_hewan         = %s
                       AND tgl_mulai_adopsi = %s
                """, [new_status, id_adopter, id_hewan, mulai_date])
        except Exception as e:
            return redirect(f'/show_message/?msg={quote(str(e))}&type=error')

        return redirect(
            'detail_adopsi',
            id_adopter=id_adopter,
            id_hewan=id_hewan,
            tgl_mulai_adopsi=tgl_mulai_adopsi
        )

    # fetch the full row plus adopter username & hewan species
    with connection.cursor() as cur:
        cur.execute("""
            SELECT
              ad.id_adopter,
              ad.id_hewan,
              ad.tgl_mulai_adopsi,
              ad.tgl_berhenti_adopsi,
              ad.kontribusi_finansial,
              ad.status_pembayaran,
              a.username_adopter,
              h.nama        AS nama_hewan,
              h.spesies     AS jenis_hewan
            FROM ADOPSI ad
            JOIN ADOPTER a
              ON a.id_adopter = ad.id_adopter
            JOIN HEWAN h
              ON h.id         = ad.id_hewan
            WHERE ad.id_adopter       = %s
              AND ad.id_hewan         = %s
              AND ad.tgl_mulai_adopsi = %s
        """, [id_adopter, id_hewan, mulai_date])
        row = cur.fetchone()

    if not row:
        return redirect('view_adopsi')

    adopsi = {
        'id_adopter':           row[0],
        'id_hewan':             row[1],
        'tgl_mulai_adopsi':     DateFormat(row[2]).format('Y-m-d'),
        'tgl_berhenti_adopsi':  DateFormat(row[3]).format('Y-m-d'),
        'kontribusi':           row[4],
        'status':               row[5],
        'adopter':              row[6],
        'nama_hewan':           row[7],
        'jenis_hewan':          row[8],
    }

    return render(request, 'detail_adopsi.html', {
        'role':   get_user_role(request.session.get('username')),
        'adopsi': adopsi
    })


@login_required_custom
@allowed_roles(['staf admin'])
def create_adopsi(request):
    if request.method == 'POST':
        id_adopter   = request.POST.get('id_adopter')
        id_hewan     = request.POST.get('id_hewan')
        periode      = int(request.POST.get('periode'))
        tgl_mulai    = date.today()
        tgl_berhenti = tgl_mulai + timedelta(days=periode*30)
        kontribusi   = int(request.POST.get('kontribusi'))
        status       = request.POST.get('status_pembayaran')
        try:
            with connection.cursor() as cur:
                cur.execute(
                    "SELECT insert_adopsi(%s, %s, %s, %s, %s, %s)",
                    [id_adopter, id_hewan, tgl_mulai, tgl_berhenti, kontribusi, status]
                )
        except Exception as e:
            return redirect(f'/show_message/?msg={quote(str(e))}&type=error')
        return redirect('view_adopsi')

    with connection.cursor() as cur:
        cur.execute("SELECT id_adopter, username_adopter FROM get_all_adopters()")
        adopters = cur.fetchall()
        cur.execute("SELECT id, nama FROM get_all_hewan()")
        hewans = cur.fetchall()

    return render(request, 'create_adopsi.html', {
        'role': get_user_role(request.session.get('username')),
        'adopters': adopters,
        'hewans': hewans
    })


@login_required_custom
@allowed_roles(['staf admin'])
def edit_adopsi(request, id_adopter, id_hewan, tgl_mulai_adopsi):
    if request.method == 'POST':
        tgl_berhenti = request.POST.get('tgl_berhenti')
        kontribusi   = request.POST.get('kontribusi')
        status       = request.POST.get('status_pembayaran')
        try:
            with connection.cursor() as cur:
                cur.execute(
                    "SELECT update_adopsi(%s, %s, %s, %s, %s, %s)",
                    [id_adopter, id_hewan, tgl_mulai_adopsi,
                     tgl_berhenti, kontribusi, status]
                )
        except Exception as e:
            return redirect(f'/show_message/?msg={quote(str(e))}&type=error')
        return redirect('view_adopsi')

    with connection.cursor() as cur:
        cur.execute(
            "SELECT * FROM get_adopsi_by_pk(%s, %s, %s)",
            [id_adopter, id_hewan, tgl_mulai_adopsi]
        )
        r = cur.fetchone()
    if not r:
        return redirect('view_adopsi')

    adopsi = {
        'id_adopter':        r[0],
        'id_hewan':          r[1],
        'tgl_mulai_adopsi':  DateFormat(r[2]).format('Y-m-d'),
        'tgl_berhenti_adopsi': DateFormat(r[3]).format('Y-m-d'),
        'kontribusi_finansial': r[4],
        'status_pembayaran': r[5],
        'username_adopter':  r[6],
        'nama_hewan':        r[7],
    }
    return render(request, 'edit_adopsi.html', {
        'role': get_user_role(request.session.get('username')),
        'adopsi': adopsi
    })


@login_required_custom
@allowed_roles(['staf admin'])
def stop_adopsi(request, id_adopter, id_hewan, tgl_mulai_adopsi):
    if request.method == 'POST':
        with connection.cursor() as cur:
            cur.execute(
                "SELECT delete_adopsi(%s, %s, %s)",
                [id_adopter, id_hewan, tgl_mulai_adopsi]
            )
        return redirect('view_adopsi')
    return render(request, 'confirm_delete_adopsi.html', {
        'role': get_user_role(request.session.get('username')),
        'id_adopter': id_adopter,
        'id_hewan': id_hewan,
        'tgl_mulai_adopsi': tgl_mulai_adopsi,
    })

@login_required_custom
@allowed_roles(['staf admin'])
def cancel_adopsi(request, id_adopter, id_hewan, tgl_mulai_adopsi):
    if request.method == 'POST':
        with connection.cursor() as cur:
            cur.execute(
                "SELECT delete_adopsi(%s, %s, %s)",
                [id_adopter, id_hewan, tgl_mulai_adopsi]
            )
        return redirect('view_adopsi')
    return render(request, 'form_batal.html', {
        'role': get_user_role(request.session.get('username')),
        'id_adopter': id_adopter,
        'id_hewan': id_hewan,
        'tgl_mulai_adopsi': tgl_mulai_adopsi,
    })


# ————————————————————
# 3. Program & Detail Adopsi (Adopter)
# ————————————————————

@login_required_custom
@allowed_roles(['pengunjung_adopter'])
def program_adopsi(request):
    adopter_id = request.session.get('adopter_id')
    with connection.cursor() as cur:
        cur.execute(
            "SELECT * FROM get_all_adopsi() WHERE id_adopter = %s",
            [adopter_id]
        )
        rows = cur.fetchall()
    adopsi_list = [
        {'id_adopter': r[0], 'id_hewan': r[1], 'tgl_mulai_adopsi': r[2],
         'tgl_berhenti_adopsi': r[3], 'kontribusi_finansial': r[4],
         'status_pembayaran': r[5]}
        for r in rows
    ]
    return render(request, 'program_adopsi.html', {
        'role': get_user_role(request.session.get('username')),
        'adopsi_list': adopsi_list
    })


@login_required_custom
@allowed_roles(['pengunjung_adopter'])
def detail_adopsi_adopter(request, id_adopter, id_hewan, tgl_mulai_adopsi):
    with connection.cursor() as cur:
        cur.execute(
            "SELECT * FROM get_adopsi_by_pk(%s, %s, %s)",
            [id_adopter, id_hewan, tgl_mulai_adopsi]
        )
        r = cur.fetchone()
    if not r:
        return redirect('program_adopsi')

    adopsi = {
        'id_adopter':        r[0],
        'id_hewan':          r[1],
        'tgl_mulai_adopsi':  DateFormat(r[2]).format('Y-m-d'),
        'tgl_berhenti_adopsi': DateFormat(r[3]).format('Y-m-d'),
        'kontribusi_finansial': r[4],
        'status_pembayaran': r[5],
    }
    return render(request, 'detail_adopsi_adopter.html', {
        'role': get_user_role(request.session.get('username')),
        'adopsi': adopsi
    })


# ————————————————————
# 4. Laporan Kondisi Satwa (Adopter)
# ————————————————————

@login_required_custom
@allowed_roles(['pengunjung_adopter'])
def laporan_kondisi(request, id_adopter, id_hewan, tgl_mulai_adopsi):
    with connection.cursor() as cur:
        cur.execute(
            "SELECT * FROM get_rekam_medis(%s, %s, %s)",
            [id_adopter, id_hewan, tgl_mulai_adopsi]
        )
        rows = cur.fetchall()
    rekam_medis = [
        {'tanggal': r[1], 'dokter': r[2], 'status': r[3], 'diagnosa': r[4], 'pengobatan': r[5], 'tindak_lanjut': r[6]}
        for r in rows
    ]
    return render(request, 'laporan_kondisi.html', {
        'role': get_user_role(request.session.get('username')),
        'rekam_medis': rekam_medis
    })


# ————————————————————
# 5. Sertifikat Adopsi (Adopter)
# ————————————————————

@login_required_custom
@allowed_roles(['pengunjung_adopter'])
def certificate_adopsi(request, id_adopter, id_hewan, tgl_mulai_adopsi):
    with connection.cursor() as cur:
        cur.execute(
            "SELECT * FROM get_adopsi_by_pk(%s, %s, %s)",
            [id_adopter, id_hewan, tgl_mulai_adopsi]
        )
        r = cur.fetchone()
    if not r:
        return redirect('program_adopsi')

    with connection.cursor() as cur:
        cur.execute("SELECT * FROM get_hewan_by_id(%s)", [r[1]])
        hw = cur.fetchone()

    sertifikat = {
        'adopter':        request.session.get('username'),
        'jenis':          hw[2] if hw else '',
        'nama_hewan':     r[7] if len(r) > 7 else '',
        'tgl_mulai':      DateFormat(r[2]).format('Y-m-d'),
        'tgl_berhenti':   DateFormat(r[3]).format('Y-m-d'),
    }
    return render(request, 'sertifikat_adopsi.html', {
        'role': get_user_role(request.session.get('username')),
        'adopsi': sertifikat
    })

@login_required_custom
@allowed_roles(['pengunjung_adopter'])
def modal_berhenti_adopter(request, id_adopter, id_hewan, tgl_mulai_adopsi):
    """
    Tampilkan modal konfirmasi berhenti adopsi, dan panggil delete_adopsi jika disubmit.
    """
    if request.method == 'POST':
        with connection.cursor() as cur:
            cur.execute(
                "SELECT delete_adopsi(%s, %s, %s)",
                [id_adopter, id_hewan, tgl_mulai_adopsi]
            )
        return redirect('program_adopsi')

    # ambil data agar bisa ditampilkan di modal
    with connection.cursor() as cur:
        cur.execute(
            "SELECT * FROM get_adopsi_by_pk(%s, %s, %s)",
            [id_adopter, id_hewan, tgl_mulai_adopsi]
        )
        r = cur.fetchone()
    if not r:
        return redirect('program_adopsi')

    adopsi = {
        'id_adopter':          r[0],
        'id_hewan':            r[1],
        'tgl_mulai_adopsi':    DateFormat(r[2]).format('Y-m-d'),
        'tgl_berhenti_adopsi': DateFormat(r[3]).format('Y-m-d'),
        'kontribusi_finansial': r[4],
        'status_pembayaran':   r[5],
        'username_adopter':    r[6],
        'nama_hewan':          r[7],
    }
    return render(request, 'modal_berhenti_adopter.html', {
        'role': get_user_role(request.session.get('username')),
        'adopsi': adopsi
    })

@login_required_custom
@allowed_roles(['pengunjung_adopter'])
def extend_adopsi(request, id_adopter, id_hewan, tgl_mulai_adopsi):
    """
    Alihkan ke detail_adopsi_adopter untuk memperpanjang.
    """
    return redirect(
        'detail_adopsi_adopter',
        id_adopter=id_adopter,
        id_hewan=id_hewan,
        tgl_mulai_adopsi=tgl_mulai_adopsi
    )

# ————————————————————
# 6–9. Statistik & Riwayat Adopter (Admin)
# ————————————————————

@login_required_custom
@allowed_roles(['staf admin'])
def daftar_adopter(request):
    totals = defaultdict(int)
    records_map = defaultdict(list)
    with connection.cursor() as cur:
        cur.execute("SELECT * FROM get_all_adopsi()")
        rows = cur.fetchall()
    for r in rows:
        # r = (id_adopter, id_hewan, tgl_mulai, tgl_berhenti, kontribusi, status_pembayaran)
        adopter = r[0]
        if adopter and r[5] == 'lunas':
            totals[adopter] += r[4]
            records_map[adopter].append({
                'id_hewan':     r[1],
                'tgl_mulai':    r[2],
                'tgl_berhenti': r[3],
                'kontribusi':   r[4],
            })
    adopters_list = [
        {'adopter': name, 'total': totals[name], 'records': records_map[name]}
        for name in totals
    ]
    adopters_list.sort(key=lambda x: x['total'], reverse=True)
    return render(request, 'halaman_daftar_adopter.html', {
        'role': get_user_role(request.session.get('username')),
        'adopters_list': adopters_list
    })


@login_required_custom
@allowed_roles(['staf admin'])
def riwayat_adopsi_adopter(request, id_adopter):
    with connection.cursor() as cur:
        cur.execute("SELECT * FROM get_adopsi_by_adopter(%s)", [id_adopter])
        rows = cur.fetchall()
    recs = [{
        'id_hewan':     r[1],
        'tgl_mulai':    r[2],
        'tgl_berhenti': r[3],
        'kontribusi':   r[4],
        'status':       r[5],
    } for r in rows]
    return render(request, 'halaman_riwayat_adopsi_adopter.html', {
        'role': get_user_role(request.session.get('username')),
        'adopter': id_adopter,
        'records': recs
    })
