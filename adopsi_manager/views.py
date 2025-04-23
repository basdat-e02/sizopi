from django.shortcuts import render, redirect

# ==== Dummy Data Adopsi ====
ADOPSI_LIST = [
    {
        "id": 1,
        "nama_hewan": "Simba",
        "jenis": "Singa Afrika",
        "kondisi": "Sehat",
        "foto_url": "https://example.com/images/simba.jpg",
        "adopter": "Ade Made",
        "status_pembayaran": "tertunda",
        "tgl_mulai": "2025-02-01",
        "tgl_berhenti": "2025-08-01",
        "kontribusi": 500000
    },
    {
        "id": 2,
        "nama_hewan": "Nala",
        "jenis": "Zebra Afrika",
        "kondisi": "Sehat",
        "foto_url": "https://example.com/images/nala.jpg",
        "adopter": None,
        "status_pembayaran": None,
        "tgl_mulai": None,
        "tgl_berhenti": None,
        "kontribusi": None
    },
    # … dst …
]

# ==== Dummy Calon Adopter ====
INDIVIDU_LIST = [
    {
        "username": "ade.made",
        "nama_depan": "Ade",
        "alamat": "Jl. Merdeka No. 10, Jakarta",
        "no_telepon": "081234567890"
    },
    {
        "username": "dewi.kartika",
        "nama_depan": "Dewi",
        "alamat": "Jl. Sultan Agung No. 33, Bali",
        "no_telepon": "082345678901"
    },
    # … tambahkan sesuai kebutuhan …
]

ORGANISASI_LIST = [
    {
        "username": "org_merak",
        "nama_org": "Merak Gacor Group",
        "npp": "2024001",
        "alamat": "Jl. Gajah Mada No. 8, Makassar",
        "no_telepon": "081298765432"
    },
    {
        "username": "org_makmur",
        "nama_org": "Makmur Group",
        "npp": "2024004",
        "alamat": "Jl. Thamrin No. 6, Palembang",
        "no_telepon": "081267890123"
    },
    # … tambahkan sesuai kebutuhan …
]


def view_adopsi(request):
    return render(request, 'view_adopsi.html', {
        "role": "staf administrasi",
        "adopsi_list": ADOPSI_LIST
    })


def create_adopsi(request, id):
    # Cari data hewan berdasarkan id
    hewan = next((h for h in ADOPSI_LIST if h["id"] == id), None)
    if not hewan:
        return redirect('view_adopsi')

    # Jika form verifikasi disubmit
    if request.method == 'POST' and 'username' in request.POST:
        username = request.POST.get('username').strip()
        jenis = request.POST.get('jenis')

        if jenis == 'individu':
            pengguna = next((u for u in INDIVIDU_LIST if u["username"] == username), None)
            if not pengguna:
                # Username tidak ditemukan → tampilkan kembali pendataan dengan pesan error
                return render(request, 'pendataan_adopter.html', {
                    "role": "staf administrasi",
                    "error": "Username tidak ditemukan atau bukan role Pengunjung.",
                    "hewan": hewan
                })
            # Lanjut ke form individu
            return render(request, 'form_individu.html', {
                "role": "staf administrasi",
                "pengguna": pengguna,
                "hewan": hewan
            })

        elif jenis == 'organisasi':
            org = next((o for o in ORGANISASI_LIST if o["username"] == username), None)
            if not org:
                return render(request, 'pendataan_adopter.html', {
                    "role": "staf administrasi",
                    "error": "Username organisasi tidak ditemukan.",
                    "hewan": hewan
                })
            # Lanjut ke form organisasi
            return render(request, 'form_organisasi.html', {
                "role": "staf administrasi",
                "pengguna": org,
                "hewan": hewan
            })

    # Untuk GET atau pertama kali, tampilkan form verifikasi (pendataan_adopter)
    return render(request, 'pendataan_adopter.html', {
        "role": "staf administrasi",
        "hewan": hewan
    })


def detail_adopsi(request, id):
    ad = next((a for a in ADOPSI_LIST if a["id"] == id), None)
    return render(request, 'detail_adopsi.html', {
        "role": "staf administrasi",
        "adopsi": ad
    })


def stop_adopsi(request, id):
    if request.method == 'POST':
        # nanti update di database
        return redirect('view_adopsi')
    ad = next((a for a in ADOPSI_LIST if a["id"] == id), None)
    return render(request, 'stop_adopsi.html', {
        "role": "staf administrasi",
        "adopsi": ad
    })

def cancel_adopsi(request, id):
    hewan = next((h for h in ADOPSI_LIST if h["id"] == id), None)
    return render(request, 'form_batal.html', {
        "role": "staf administrasi",
        "hewan_id": id,
        "hewan": hewan,
    })