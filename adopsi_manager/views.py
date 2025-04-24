# views.py
from django.shortcuts import render, redirect
from collections import defaultdict
from django.utils import timezone



ADOPSI_LIST = [
    {
        "id": 1,
        "nama_hewan": "Simba",
        "jenis": "Singa Afrika",
        "kondisi": "Sehat",
        "foto_url": "https://…/simba.jpg",
        "adopter": "Ade Made",
        "habitat": "Savana",
        "status_pembayaran": "lunas",
        "tgl_mulai": "2025-01-01",
        "tgl_berhenti": "2025-07-01",
        "kontribusi": 500_000
    },
    {
        "id": 2,
        "nama_hewan": "Nala",
        "jenis": "Zebra Afrika",
        "kondisi": "Sehat",
        "foto_url": "https://…/nala.jpg",
        "adopter": "Cindy",
        "habitat": "Savana",
        "status_pembayaran": "lunas",
        "tgl_mulai": "2024-12-12",
        "tgl_berhenti": "2025-12-12",
        "kontribusi": 1_200_000
    },
    {
        "id": 3,
        "nama_hewan": "Melly",
        "jenis": "Gajah Sumatra",
        "kondisi": "Sehat",
        "foto_url": "https://…/melly.jpg",
        "adopter": "Bambang",
        "habitat": "Hutan Tropis",
        "status_pembayaran": "lunas",
        "tgl_mulai": "2025-02-26",
        "tgl_berhenti": "2025-08-26",
        "kontribusi": 850_000
    },
    {
        "id": 4,
        "nama_hewan": "Rio",
        "jenis": "Harimau Kalimantan",
        "kondisi": "Sakit",
        "foto_url": "https://…/rio.jpg",
        "adopter": "Bambang",
        "habitat": "Hutan Tropis",
        "status_pembayaran": "lunas",
        "tgl_mulai": "2023-01-01",
        "tgl_berhenti": "2023-07-01",
        "kontribusi": 800_000
    },
    {
        "id": 5,
        "nama_hewan": "Bimo",
        "jenis": "Orangutan",
        "kondisi": "Sehat",
        "foto_url": "https://…/bimo.jpg",
        "adopter": "Dewi Kartika",
        "habitat": "Hutan Tropis",
        "status_pembayaran": "lunas",
        "tgl_mulai": "2024-07-10",
        "tgl_berhenti": "2024-10-10",
        "kontribusi": 500_000
    },
    
]


# ==== Dummy Calon Adopter untuk staf administrasi ==== 
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
    # … tambahkan jika perlu … 
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
    # … tambahkan jika perlu … 
]

def view_adopsi(request):
    return render(request, 'view_adopsi.html', {
        "role": "staf administrasi",
        "adopsi_list": ADOPSI_LIST
    })

def create_adopsi(request, id):
    hewan = next((h for h in ADOPSI_LIST if h["id"] == id), None)
    if not hewan:
        return redirect('view_adopsi')

    # verifikasi username & jenis
    if request.method == 'POST' and 'username' in request.POST:
        username = request.POST['username'].strip()
        jenis    = request.POST['jenis']

        if jenis == 'individu':
            pengguna = next((u for u in INDIVIDU_LIST if u["username"] == username), None)
            if not pengguna:
                return render(request, 'pendataan_adopter.html', {
                    "role": "staf administrasi",
                    "error": "Username tidak ditemukan atau bukan role Pengunjung.",
                    "hewan": hewan
                })
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
            return render(request, 'form_organisasi.html', {
                "role": "staf administrasi",
                "pengguna": org,
                "hewan": hewan
            })

    # pertama kali atau GET
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
        # nanti update ke DB
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
        "hewan": hewan
    })

def program_adopsi(request):
    return render(request, 'program_adopsi.html', {
        "role": "pengunjung",
        "adopsi_list": ADOPSI_LIST
    })

def detail_adopsi_adopter(request, id):
    # cari data adopsi berdasarkan id
    ad = next((a for a in ADOPSI_LIST if a["id"] == id), None)
    if not ad:
        # jika tidak ada, balik ke daftar
        return redirect('program_adopsi')

    return render(request, 'detail_adopsi_adopter.html', {
        "role": "pengunjung",
        "adopsi": ad
    })
    
# Dummy data rekam medis untuk laporan kondisi
MEDIS_LIST = [
    {"hewan_id": 1, "tanggal": "2025-02-15", "dokter": "Dr. Siti Aminah", "status": "Sehat",    "diagnosa": "–",       "pengobatan": "–",        "tindak_lanjut": "–"},
    {"hewan_id": 1, "tanggal": "2025-04-01", "dokter": "Dr. Siti Aminah", "status": "Sakit",    "diagnosa": "Infeksi pernapasan", "pengobatan": "Antibiotik 7 hari", "tindak_lanjut": "Ventilasi kandang diperbaiki"},
    {"hewan_id": 2, "tanggal": "2025-03-05", "dokter": "Dr. Budi Santoso","status": "Dalam Pemantauan", "diagnosa": "–","pengobatan": "–","tindak_lanjut": "Pantau rutin"},
    # … dst …
]

def laporan_kondisi(request, id):
    # cari hewan di daftar adopsi
    ad = next((a for a in ADOPSI_LIST if a["id"] == id), None)
    if not ad or not ad["adopter"]:
        return redirect('program_adopsi')
    # filter rekam medis setelah tgl_mulai
    tgl_mulai = ad["tgl_mulai"]
    records = [m for m in MEDIS_LIST 
               if m["hewan_id"] == id and m["tanggal"] >= tgl_mulai]
    return render(request, 'laporan_kondisi.html', {
        "role": "pengunjung",
        "adopsi": ad,
        "rekam_medis": records
    })
    
def certificate_adopsi(request, id):
    # find the adoption record
    ad = next((a for a in ADOPSI_LIST if a["id"] == id), None)
    # only proceed if it exists and has an adopter
    if not ad or not ad["adopter"]:
        return redirect('program_adopsi')

    return render(request, 'sertifikat_adopsi.html', {
        "role": "pengunjung",
        "adopsi": ad
    })

def extend_adopsi(request, id):
    # find the adoption record
    ad = next((a for a in ADOPSI_LIST if a["id"] == id), None)
    if not ad or not ad["adopter"]:
        return redirect('program_adopsi')

    # what kind of extension? must be passed as ?type=individu or ?type=organisasi
    extend_type = request.GET.get('type')
    if extend_type not in ('individu', 'organisasi'):
        # if no type, bounce back to detail
        return redirect('detail_adopsi_adopter', id=id)

    if request.method == 'POST':
        # here you’d process the form submission (update ad["kontribusi"], tgl_berhenti, etc)
        return redirect('detail_adopsi_adopter', id=id)

    # choose the right template and context
    if extend_type == 'individu':
        # find the individual adopter data by matching the name
        pengguna = next((u for u in INDIVIDU_LIST if u["nama_depan"] in ad["adopter"]), {})
        return render(request, 'perpanjang_adopsi_individu.html', {
            "role": "pengunjung",
            "hewan": ad,
            "pengguna": pengguna
        })
    else:  # organisasi
        pengguna = next((o for o in ORGANISASI_LIST if o["nama_org"] in ad["adopter"]), {})
        return render(request, 'perpanjang_adopsi_organisasi.html', {
            "role": "pengunjung",
            "hewan": ad,
            "pengguna": pengguna
        })
    
def modal_berhenti_adopter(request, id):
    ad = next((a for a in ADOPSI_LIST if a["id"] == id), None)
    if not ad or not ad["adopter"]:
        return redirect('program_adopsi')
    return render(request, 'modal_berhenti_adopter.html', {
        "role": "pengunjung",
        "adopsi": ad
    })
    
def daftar_adopter(request):
    # group by adopter and sum kontribusi
    totals = defaultdict(int)
    records = defaultdict(list)
    for a in ADOPSI_LIST:
        if a["adopter"] and a["status_pembayaran"] == "lunas":
            totals[a["adopter"]] += a["kontribusi"]
            records[a["adopter"]].append(a)

    adopters = [
        {"nama": name, "total": total, "records": records[name]}
        for name, total in totals.items()
    ]
    adopters.sort(key=lambda x: x["total"], reverse=True)

    top5 = adopters[:5]

    return render(request, "halaman_daftar_adopter.html", {
        "role": "staf administrasi",
        "top5": top5,
        "adopters": adopters
    })


def riwayat_adopsi_adopter(request, nama):
    # filter only this adopter’s records (lunas or ongoing)
    recs = [a for a in ADOPSI_LIST if a["adopter"] == nama and a["status_pembayaran"] == "lunas"]

    # find contact info (fallback to placeholders)
    contact = {"nama": nama, "alamat": "-", "no_telepon": "-"}
    # if you have detailed INDIVIDU_LIST/ORGANISASI_LIST, you can look it up here

    # determine “today” for ongoing vs. ended
    today = timezone.now().date().isoformat()

    return render(request, "halaman_riwayat_adopsi_adopter.html", {
        "role": "staf administrasi",
        "adopter": nama,
        "contact": contact,
        "records": recs,
        "today": today
    })
