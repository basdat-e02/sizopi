from gettext import translation
from pyexpat.errors import messages
from shlex import quote
from urllib.parse import quote_plus
import uuid
from datetime import date, timedelta
from collections import defaultdict
from datetime import datetime
from django.shortcuts import render, redirect
from django.db import IntegrityError, connection
from django.utils import timezone
from django.utils.dateformat import DateFormat
from django.http import Http404  
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
    role = get_user_role(request.session.get('username'))

    # STEP 1: Lookup akun pengunjung + render form detail
    if request.method == 'POST' and request.POST.get('step') == 'lookup':
        username = request.POST.get('username', '').strip()
        jenis    = request.POST.get('jenis')  # 'individu' atau 'organisasi'

        # ambil data pengunjung + nama_depan, alamat, no_telepon
        with connection.cursor() as cur:
            cur.execute("""
                SELECT p.alamat, u.nama_depan, u.no_telepon
                  FROM PENGUNJUNG p
                  JOIN PENGGUNA  u ON u.username = p.username_P
                 WHERE p.username_P = %s
            """, [username])
            row = cur.fetchone()

        if not row:
            return render(request, 'pendataan_adopter.html', {
                'role':     role,
                'id_hewan': id_hewan,
                'error':    f"Username “{username}” belum terdaftar sebagai pengunjung."
            })

        alamat, nama_depan, no_telepon = row

        # ambil data hewan
        with connection.cursor() as cur:
            cur.execute("SELECT nama, spesies FROM HEWAN WHERE id = %s", [id_hewan])
            hewan = cur.fetchone()
        if not hewan:
            return redirect('view_adopsi')
        nama_hewan, jenis_hewan = hewan

        ctx = {
            'role':         role,
            'id_hewan':     id_hewan,
            'username':     username,
            'nama_depan':   nama_depan,
            'alamat':       alamat,
            'no_telepon':   no_telepon,
            'nama_hewan':   nama_hewan,
            'jenis_hewan':  jenis_hewan,
            'jenis':        jenis,
        }
        template = 'form_individu.html' if jenis == 'individu' else 'form_organisasi.html'
        return render(request, template, ctx)

    # STEP 2: Setelah isi detail & kontribusi, create or reuse adopter + insert adopsi
    if request.method == 'POST' and request.POST.get('step') == 'create':
        username    = request.POST['username']
        jenis       = request.POST['jenis']
        kontribusi  = int(request.POST['kontribusi'])
        periode     = int(request.POST['periode'])  # misal 3,6,12
        mulai       = date.today()
        berhenti    = mulai + timedelta(days=periode*30)

        with connection.cursor() as cur:
            # 2a) cek apakah sudah ada di ADOPTER
            cur.execute("SELECT id_adopter FROM ADOPTER WHERE username_adopter = %s", [username])
            r = cur.fetchone()
            if r:
                id_adopter = r[0]
            else:
                id_adopter = str(uuid.uuid4())
                cur.execute(
                    "INSERT INTO ADOPTER (id_adopter, username_adopter, total_kontribusi) VALUES (%s,%s,0)",
                    [id_adopter, username]
                )
                # juga simpan detail INDIVIDU/ORGANISASI
                if jenis == 'individu':
                    nik  = request.POST['nik']
                    nama = request.POST['nama']
                    cur.execute(
                        "INSERT INTO INDIVIDU (nik, nama, id_adopter) VALUES (%s,%s,%s)",
                        [nik, nama, id_adopter]
                    )
                else:
                    npp      = request.POST['npp']
                    nama_org = request.POST['nama_org']
                    cur.execute(
                        "INSERT INTO ORGANISASI (npp, nama_organisasi, id_adopter) VALUES (%s,%s,%s)",
                        [npp, nama_org, id_adopter]
                    )

            # 2b) insert ke ADOPSI
            cur.execute("""
                INSERT INTO ADOPSI
                  (id_adopter, id_hewan, tgl_mulai_adopsi, tgl_berhenti_adopsi,
                   kontribusi_finansial, status_pembayaran)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, [id_adopter, id_hewan, mulai, berhenti, kontribusi, 'Pending'])

        return redirect('view_adopsi')

    # STEP 0: GET awal → lookup form
    return render(request, 'pendataan_adopter.html', {
        'role':     role,
        'id_hewan': id_hewan,
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
@allowed_roles(['pengunjung', 'pengunjung_adopter'])
def program_adopsi(request):
    adopter_id = request.session.get('adopter_id')

    with connection.cursor() as cur:
        cur.execute("""
            SELECT id, nama, spesies, status_kesehatan, url_foto
              FROM HEWAN
             ORDER BY nama
        """)
        hewan_rows = cur.fetchall()

    adopsi_list = []
    with connection.cursor() as cur:
        for id_hewan, nama, jenis, kondisi, url_foto in hewan_rows:
            cur.execute("""
                SELECT tgl_mulai_adopsi
                  FROM ADOPSI
                 WHERE id_adopter = %s
                   AND id_hewan   = %s
            """, [adopter_id, id_hewan])
            row = cur.fetchone()

            if row:
                tgl = row[0].strftime('%Y-%m-%d')
                adopsi_list.append({
                    'id_adopter':       adopter_id,
                    'id_hewan':         id_hewan,
                    'tgl_mulai_adopsi': tgl,
                    'foto_url':         url_foto,
                    'nama_hewan':       nama,
                    'jenis':            jenis,
                    'kondisi':          kondisi,
                })
            else:
                adopsi_list.append({
                    'id_adopter':       None,
                    'id_hewan':         id_hewan,
                    'tgl_mulai_adopsi': None,
                    'foto_url':         url_foto,
                    'nama_hewan':       nama,
                    'jenis':            jenis,
                    'kondisi':          kondisi,
                })

    return render(request, 'program_adopsi.html', {
        'role':        get_user_role(request.session.get('username')),
        'adopsi_list': adopsi_list,
    })


@login_required_custom
@allowed_roles(['pengunjung', 'pengunjung_adopter'])
def program_adopsi(request):
    username = request.session['username']
    # Cari id_adopter dari username
    with connection.cursor() as cur:
        cur.execute("SELECT id_adopter FROM ADOPTER WHERE username_adopter = %s", [username])
        row = cur.fetchone()
    adopter_id = row[0] if row else None

    # Ambil semua hewan
    with connection.cursor() as cur:
        cur.execute("""
            SELECT id, nama, spesies, status_kesehatan, url_foto
            FROM HEWAN
            ORDER BY nama
        """)
        hewan_rows = cur.fetchall()

    adopsi_list = []
    with connection.cursor() as cur:
        for id_hewan, nama, spesies, kondisi, foto_url in hewan_rows:
            # cek adopsi
            tgl_mulai = None
            if adopter_id:
                cur.execute("""
                    SELECT tgl_mulai_adopsi
                    FROM ADOPSI
                    WHERE id_adopter = %s AND id_hewan = %s
                """, [adopter_id, id_hewan])
                r = cur.fetchone()
                if r:
                    tgl_mulai = r[0].strftime('%Y-%m-%d')
            if tgl_mulai:
                adopsi_list.append({
                    'id_adopter':       adopter_id,
                    'id_hewan':         id_hewan,
                    'tgl_mulai_adopsi': tgl_mulai,
                    'nama_hewan':       nama,
                    'jenis':            spesies,
                    'kondisi':          kondisi,
                    'foto_url':         foto_url,
                })

    return render(request, 'program_adopsi.html', {
        'role':         get_user_role(request.session.get('username')),
        'adopsi_list':  adopsi_list,   
    })


@login_required_custom
@allowed_roles(['pengunjung_adopter'])
def detail_adopsi_adopter(request, id_adopter, id_hewan, tgl_mulai_adopsi):
    # parsing tanggal
    mulai_date = datetime.strptime(tgl_mulai_adopsi, '%Y-%m-%d').date()

    # ambil detail adopsi + info hewan
    with connection.cursor() as cur:
        cur.execute("""
            SELECT
              ad.id_adopter,
              ad.id_hewan,
              ad.tgl_mulai_adopsi,
              ad.tgl_berhenti_adopsi,
              ad.kontribusi_finansial,
              ad.status_pembayaran,
              h.nama         AS nama_hewan,
              h.spesies      AS jenis,
              h.nama_habitat AS habitat
            FROM ADOPSI ad
            JOIN HEWAN h ON h.id = ad.id_hewan
            WHERE ad.id_adopter = %s
              AND ad.id_hewan   = %s
              AND ad.tgl_mulai_adopsi = %s
        """, [id_adopter, id_hewan, mulai_date])
        r = cur.fetchone()

    if not r:
        return redirect('program_adopsi')

    adopsi = {
        'id_adopter':           r[0],
        'id_hewan':             r[1],
        'tgl_mulai_adopsi':     DateFormat(r[2]).format('Y-m-d'),
        'tgl_berhenti_adopsi':  DateFormat(r[3]).format('Y-m-d'),
        'kontribusi_finansial': r[4],
        'status_pembayaran':    r[5],
        'nama_hewan':           r[6],
        'jenis':                r[7],
        'habitat':              r[8],
    }

    return render(request, 'detail_adopsi_adopter.html', {
        'role':   get_user_role(request.session.get('username')),
        'adopsi': adopsi,
    })

# ————————————————————
# 4. Laporan Kondisi Satwa (Adopter)
# ————————————————————

@login_required_custom
@allowed_roles(['pengunjung', 'pengunjung_adopter'])
def laporan_kondisi(request, id_adopter, id_hewan, tgl_mulai_adopsi):
    # ambil data hewan & adopsi seperti yang sudah kamu punya...
    with connection.cursor() as cur:
        # contoh mengambil data medis
        cur.execute("""
            SELECT tanggal_pemeriksaan, username_dh, status_kesehatan,
                   diagnosis, pengobatan, catatan_tindak_lanjut
              FROM CATATAN_MEDIS
             WHERE id_hewan = %s
          ORDER BY tanggal_pemeriksaan DESC
        """, [id_hewan])
        medis = [
            {
                'tanggal': row[0],
                'dokter':  row[1],
                'status':  row[2],
                'diagnosa':row[3],
                'pengobatan': row[4],
                'catatan': row[5],
            }
            for row in cur.fetchall()
        ]

    return render(request, 'laporan_kondisi.html', {
        'role': get_user_role(request.session.get('username')),
        'medis_list': medis,
        # yang hilang:
        'id_adopter':      id_adopter,
        'id_hewan':        id_hewan,
        'tgl_mulai_adopsi': tgl_mulai_adopsi,
    })

# ————————————————————
# 5. Sertifikat Adopsi (Adopter)
# ————————————————————

@login_required_custom
@allowed_roles(['pengunjung_adopter'])
def certificate_adopsi(request, id_adopter, id_hewan, tgl_mulai_adopsi):
    # ambil data adopsi & adopter info & hewan
    with connection.cursor() as cur:
        cur.execute("SELECT * FROM get_adopsi_by_pk(%s,%s,%s)",
                    [id_adopter, id_hewan, tgl_mulai_adopsi])
        r = cur.fetchone()
        if not r:
            return redirect('program_adopsi')
        # r = (id_adopter,id_hewan,tgl_mulai,tgl_berhenti,kontrib, status)
        mulai, akhir = r[2], r[3]
        # adopter detail: cek individu dulu
        cur.execute("SELECT nama, nik FROM INDIVIDU WHERE id_adopter = %s", [id_adopter])
        ind = cur.fetchone()
        if ind:
            nama_adopter = ind[0]
        else:
            cur.execute("SELECT nama_organisasi FROM ORGANISASI WHERE id_adopter = %s", [id_adopter])
            nama_adopter = cur.fetchone()[0]
        # hewan
        cur.execute("SELECT nama, spesies FROM HEWAN WHERE id = %s", [id_hewan])
        nama_hewan, jenis = cur.fetchone()

    ctx = {
        'nama_adopter': nama_adopter,
        'nama_hewan':   nama_hewan,
        'jenis':        jenis,
        'tgl_mulai':    DateFormat(mulai).format('Y-m-d'),
        'tgl_berhenti': DateFormat(akhir).format('Y-m-d'),
    }
    return render(request, 'sertifikat_adopsi.html', ctx)


@login_required_custom
@allowed_roles(['pengunjung_adopter'])
def modal_berhenti_adopter(request, id_adopter, id_hewan, tgl_mulai_adopsi):
    # Immediately delete the adoption and send back to program_adopsi
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
@login_required_custom
@allowed_roles(['pengunjung_adopter'])
def extend_adopsi(request, id_adopter, id_hewan, tgl_mulai_adopsi):
    # 1. Parse tanggal mulai
    try:
        mulai_date = datetime.strptime(tgl_mulai_adopsi, '%Y-%m-%d').date()
    except ValueError:
        raise Http404("Format tanggal tidak valid")

    # 2. Cek tipe dan ambil data pengguna + hewan (sama seperti sebelumnya)
    with connection.cursor() as cur:
        cur.execute("SELECT nik FROM INDIVIDU WHERE id_adopter = %s", [id_adopter])
        is_individu = bool(cur.fetchone())
        if is_individu:
            cur.execute("""
                SELECT u.nama_depan, p.alamat, u.no_telepon
                  FROM PENGUNJUNG p
                  JOIN PENGGUNA u       ON u.username = p.username_P
                  JOIN ADOPTER a        ON a.username_adopter = p.username_P
                 WHERE a.id_adopter = %s
            """, [id_adopter])
        else:
            cur.execute("""
                SELECT o.nama_organisasi, COALESCE(p.alamat,''), u.no_telepon
                  FROM ORGANISASI o
                  JOIN ADOPTER    a     ON a.id_adopter = o.id_adopter
                  LEFT JOIN PENGUNJUNG p ON p.username_P = a.username_adopter
                  JOIN PENGGUNA    u     ON u.username = a.username_adopter
                 WHERE o.id_adopter = %s
            """, [id_adopter])
        pengguna_row = cur.fetchone()
        if not pengguna_row:
            raise Http404("Data pengguna tidak ditemukan")
        nama_depan, alamat, no_telepon = pengguna_row

        cur.execute("SELECT nama, spesies FROM HEWAN WHERE id = %s", [id_hewan])
        hewan_row = cur.fetchone()
        if not hewan_row:
            raise Http404("Data hewan tidak ditemukan")
        nama_hewan, jenis_hewan = hewan_row

    # 3. Context untuk template
    ctx = {
        'role':             get_user_role(request.session.get('username')),
        'id_adopter':       id_adopter,
        'id_hewan':         id_hewan,
        'tgl_mulai_adopsi': tgl_mulai_adopsi,
        'pengguna': {
            'nama_depan': nama_depan,
            'alamat':     alamat,
            'no_telepon': no_telepon,
        },
        'hewan': {
            'nama_hewan': nama_hewan,
            'jenis':      jenis_hewan,
        },
    }

    # 4. Proses POST: update dan redirect
    if request.method == 'POST':
        try:
            periode = int(request.POST['periode'])
            kontrib = int(request.POST['kontribusi'])
        except (KeyError, ValueError):
            ctx['error'] = "Periode & kontribusi harus berupa angka."
            template = 'perpanjang_adopsi_individu.html' if is_individu else 'perpanjang_adopsi_organisasi.html'
            return render(request, template, ctx)

        tambahan_hari = periode * 30
        with connection.cursor() as cur:
            cur.execute("""
                UPDATE ADOPSI
                   SET tgl_berhenti_adopsi  = tgl_berhenti_adopsi + INTERVAL '%s days',
                       kontribusi_finansial = kontribusi_finansial + %s
                 WHERE id_adopter         = %s
                   AND id_hewan           = %s
                   AND tgl_mulai_adopsi    = %s
            """, [tambahan_hari, kontrib, id_adopter, id_hewan, mulai_date])

        # **Gunakan positional args di sini** agar tidak keliru menjadi satu arg kosong  
        return redirect(
            'detail_adopsi_adopter',
            id_adopter,
            id_hewan,
            tgl_mulai_adopsi
        )

    # 5. Render GET form
    template = 'perpanjang_adopsi_individu.html' if is_individu else 'perpanjang_adopsi_organisasi.html'
    return render(request, template, ctx)

# ————————————————————
# 6–9. Statistik & Riwayat Adopter (Admin)
# ————————————————————
from urllib.parse import quote_plus
from django.db import connection, IntegrityError, transaction as db_tx

@login_required_custom
@allowed_roles(['staf admin'])
def daftar_adopter(request):
    # =================================================
    # A.  HANDLE POST  ➜ hapus adopter
    # =================================================
    if request.method == "POST":
        adopter_id = request.POST.get("adopter_id")
        if adopter_id:
            try:
                with db_tx.atomic(), connection.cursor() as cur:
                    # 1️⃣  Hapus relasi individu / organisasi (kalau ada)
                    cur.execute("DELETE FROM individu   WHERE id_adopter = %s",
                                [adopter_id])
                    cur.execute("DELETE FROM organisasi WHERE id_adopter = %s",
                                [adopter_id])

                    # 2️⃣  Cek adopsi AKTIF
                    cur.execute("""
                        SELECT 1
                        FROM adopsi
                        WHERE id_adopter = %s
                        AND CURRENT_DATE BETWEEN tgl_mulai_adopsi
                                            AND tgl_berhenti_adopsi
                        LIMIT 1
                    """, [adopter_id])
                    if cur.fetchone():
                        raise ValueError(
                            "Adopter masih aktif berpartisipasi. "
                            "Data tidak bisa dihapus."
                        )

                    # 3️⃣  Hapus adopsi selesai & lunas
                    cur.execute("""
                        DELETE FROM adopsi
                        WHERE id_adopter = %s
                        AND status_pembayaran ILIKE 'lunas'
                        AND CURRENT_DATE > tgl_berhenti_adopsi
                    """, [adopter_id])

                    # 4️⃣  Hapus adopter (sekarang FK sudah bersih)
                    cur.execute("DELETE FROM adopter WHERE id_adopter = %s",
                                [adopter_id])

            except IntegrityError:
                msg = ("Adopter masih terhubung dengan data lain. "
                    "Pastikan semua relasi sudah dihapus.")
                return redirect(
                    f"/show_message/?msg={quote_plus(msg)}"
                    f"&type=error&next_url=daftar_adopter"
                )
            except ValueError as e:
                return redirect(
                    f"/show_message/?msg={quote_plus(str(e))}"
                    f"&type=warning&next_url=daftar_adopter"
                )

            msg = "Adopter dan data terkait berhasil dihapus."
            return redirect(
                f"/show_message/?msg={quote_plus(msg)}"
                f"&type=success&next_url=daftar_adopter"
            )



    # =================================================
    # B.  GET  ➜ tampilkan daftar
    # =================================================
    # --- GET: ambil data adopter + agregat langsung, TANPA view -------------
    with connection.cursor() as cur:
        cur.execute("""
            WITH a AS (
                SELECT  id_adopter,
                        SUM(CASE WHEN status_pembayaran ILIKE 'lunas'
                                THEN kontribusi_finansial ELSE 0 END)         AS total_lunas,
                        SUM(CASE WHEN status_pembayaran ILIKE 'lunas'
                                AND tgl_mulai_adopsi >= CURRENT_DATE - INTERVAL '1 year'
                                THEN kontribusi_finansial ELSE 0 END)         AS last_year_lunas,
                        BOOL_OR (CURRENT_DATE BETWEEN tgl_mulai_adopsi
                                                AND tgl_berhenti_adopsi)       AS masih_aktif
                FROM    adopsi
                GROUP   BY id_adopter
            )
            SELECT  ad.id_adopter,
                    COALESCE(i.nama, o.nama_organisasi)            AS nama,
                    CASE WHEN i.id_adopter IS NOT NULL
                        THEN 'individu' ELSE 'organisasi' END     AS tipe,
                    a.total_lunas,
                    a.last_year_lunas,
                    a.masih_aktif
            FROM    adopter ad
            JOIN    a ON a.id_adopter = ad.id_adopter      -- hanya adopter yg pernah lunas
            LEFT    JOIN individu   i ON i.id_adopter = ad.id_adopter
            LEFT    JOIN organisasi o ON o.id_adopter = ad.id_adopter
            WHERE   a.total_lunas > 0                      -- buang kontribusi 0
        """)
        rows = cur.fetchall()
        # kolom: (id_adopter, nama, tipe, total_lunas,
        #         last_year_lunas, masih_aktif)


    individu, organisasi = [], []
    for r in rows:
        data = {
            "id":    r[0],
            "nama":  r[1],
            "total": r[3] or 0,
            "aktif": r[5],
        }
        (individu if r[2] == "individu" else organisasi).append(data)

    # ---------- TOP-5 hanya yg punya last_year_lunas > 0 ----------
    tahun_ini = [r for r in rows if (r[4] or 0) > 0]
    tahun_ini.sort(key=lambda r: r[4], reverse=True)
    top5 = [{"nama": r[1], "total": r[4]} for r in tahun_ini[:5]]

    return render(request, "halaman_daftar_adopter.html", {
        "role":                 get_user_role(request.session.get("username")),
        "adopters_individu":    individu,
        "adopters_organisasi":  organisasi,
        "top5":                 top5,                 # ← bisa kosong []
    })

@login_required_custom
@allowed_roles(['staf admin'])
def riwayat_adopsi_adopter(request, id_adopter):

    # ===============================================================
    # A.  HANDLE POST  → hapus adopsi
    # ===============================================================
    if request.method == "POST":
        id_hewan   = request.POST.get("id_hewan")
        tgl_mulai  = request.POST.get("tgl_mulai")        # YYYY-MM-DD

        try:
            with connection.cursor() as cur:
                # pastikan baris itu memang boleh dihapus
                cur.execute("""
                    SELECT 1
                      FROM adopsi
                     WHERE id_adopter = %s
                       AND id_hewan   = %s
                       AND tgl_mulai_adopsi = %s
                       AND status_pembayaran ILIKE 'lunas'
                       AND CURRENT_DATE > tgl_berhenti_adopsi
                     LIMIT 1
                """, [id_adopter, id_hewan, tgl_mulai])

                if not cur.fetchone():
                    raise ValueError("Data adopsi masih berlangsung "
                                     "atau belum lunas.")

                # hapus
                cur.execute("""
                    DELETE FROM adopsi
                     WHERE id_adopter = %s
                       AND id_hewan   = %s
                       AND tgl_mulai_adopsi = %s
                """, [id_adopter, id_hewan, tgl_mulai])

        except ValueError as e:
            return redirect(
                f"/show_message/?msg={quote_plus(str(e))}"
                f"&type=warning&next_url=/riwayat-adopsi/{id_adopter}/"
            )
        except IntegrityError:
            msg = "Gagal menghapus. Silakan coba lagi."
            return redirect(
                f"/show_message/?msg={quote_plus(msg)}"
                f"&type=error&next_url=/riwayat-adopsi/{id_adopter}/"
            )

        # sukses
        return redirect(
            f"/show_message/?msg={quote_plus('Data adopsi berhasil dihapus.')}"
            f"&type=success&next_url=/riwayat-adopsi/{id_adopter}/"
        )

    # ===============================================================
    # B.  GET  → tampilkan riwayat
    # ===============================================================
    with connection.cursor() as cur:
        # — info kontak adopter —
        cur.execute("""
            SELECT
              COALESCE(i.nama, o.nama_organisasi)      AS nama,
              p.alamat,
              g.no_telepon
            FROM adopter ad
            LEFT JOIN individu   i ON i.id_adopter = ad.id_adopter
            LEFT JOIN organisasi o ON o.id_adopter = ad.id_adopter
            LEFT JOIN pengunjung p ON p.username_p  = ad.username_adopter
            LEFT JOIN pengguna   g ON g.username    = ad.username_adopter
            WHERE ad.id_adopter = %s
            LIMIT 1
        """, [id_adopter])
        contact_row = cur.fetchone() or ("-", "-", "-")
        contact = {
            "nama":       contact_row[0],
            "alamat":     contact_row[1],
            "no_telepon": contact_row[2],
        }

        # — daftar adopsi lunas (selesai & berlangsung) —
        cur.execute("""
            SELECT
              h.nama,
              h.spesies,
              a.id_hewan,
              a.tgl_mulai_adopsi,
              a.tgl_berhenti_adopsi,
              a.kontribusi_finansial
            FROM adopsi a
            JOIN hewan h ON h.id = a.id_hewan
            WHERE a.id_adopter = %s
              AND a.status_pembayaran ILIKE 'lunas'
            ORDER BY a.tgl_mulai_adopsi DESC
        """, [id_adopter])
        rows = cur.fetchall()

    records = [{
        "nama_hewan"  : r[0],
        "jenis"       : r[1],
        "id_hewan"    : r[2],
        "tgl_mulai"   : r[3],
        "tgl_berhenti": r[4],
        "kontribusi"  : r[5],
        "boleh_hapus" : date.today() > r[4],     # true kalau periode selesai
    } for r in rows]

    return render(request, "halaman_riwayat_adopsi_adopter.html", {
        "role"    : get_user_role(request.session.get("username")),
        "contact" : contact,
        "records" : records,
        "today"   : date.today(),
        "id_adopter": id_adopter,               # utk path kembali
    })
