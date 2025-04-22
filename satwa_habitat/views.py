from django.shortcuts import render

# Create your views here.

from django.shortcuts import render

def view_satwa(request):
    satwa_list = [
        {
            "id": 1,
            "nama": "Simba",
            "spesies": "Singa",
            "asal": "Afrika",
            "tanggal_lahir": "2018-05-12",
            "status": "Sehat",
            "habitat": "Savana",
        },
        {
            "id": 2,
            "nama": "Melly",
            "spesies": "Gajah",
            "asal": "Sumatra",
            "tanggal_lahir": "2015-09-22",
            "status": "Dalam Pemantauan",
            "habitat": "Hutan Tropis",
        },
        {
            "id": 3,
            "nama": "Rio",
            "spesies": "Harimau",
            "asal": "Kalimantan",
            "tanggal_lahir": "2015-09-22",
            "status": "Sakit",
            "habitat": "Hutan Tropis",
        },
        {
            "id": 4,
            "nama": "Nala",
            "spesies": "Zebra",
            "asal": "Afrika",
            "tanggal_lahir": "2020-03-01",
            "status": "Sehat",
            "habitat": "Savana",
        },
        {
            "id": 5,
            "nama": "Bimo",
            "spesies": "Orangutan",
            "asal": "Kalimantan",
            "tanggal_lahir": "2016-07-19",
            "status": "Sehat",
            "habitat": "Hutan Tropis",
        },
    ]

    context = {
        "role": "penjaga hewan",
        "satwa_list": satwa_list,
    }
    return render(request, 'view_satwa.html', context)


def create_satwa(request):
    context = {
        "role": "penjaga hewan"
    }
    return render(request, 'create_satwa.html', context)

def edit_satwa(request, id):
    context = {
        "role": "penjaga hewan"
    }
    return render(request, 'edit_satwa.html', context)

def view_habitat(request):
    habitat_list = [
        {
            "id": 1,
            "nama": "Savana",
            "luas": 5000,
            "kapasitas": 20,
            "status": "Suhu: 30°C, Kelembapan: 40%, Vegetasi padang rumput"
        },
        {
            "id": 2,
            "nama": "Hutan Tropis",
            "luas": 7500,
            "kapasitas": 30,
            "status": "Suhu: 27°C, Kelembapan: 80%, Vegetasi lebat"
        },
        {
            "id": 3,
            "nama": "Kolam Air Tawar",
            "luas": 2500,
            "kapasitas": 15,
            "status": "Suhu: 22°C, pH: 7.2, Air jernih"
        },
        {
            "id": 4,
            "nama": "Gurun",
            "luas": 4000,
            "kapasitas": 10,
            "status": "Suhu: 40°C, Kelembapan: 20%, Minim vegetasi"
        },
        {
            "id": 5,
            "nama": "Pegunungan",
            "luas": 6000,
            "kapasitas": 18,
            "status": "Suhu: 18°C, Kelembapan: 60%, Berbatu dan hutan pinus"
        }
    ]

    context = {
        "role": "penjaga hewan",
        "habitat_list": habitat_list
    }
    return render(request, 'view_habitat.html', context)


def detail_habitat(request, id):
    habitat = {
        "id": id,
        "nama": "Savana",
        "luas": 5000,
        "kapasitas": 20,
        "status": "Suhu: 30°C, Kelembapan: 40%, Vegetasi padang rumput"
    }

    hewan_list = [
        {"nama": "Simba", "spesies": "Singa", "asal": "Afrika", "tanggal_lahir": "2018-05-12", "status": "Sehat"},
        {"nama": "Nala", "spesies": "Zebra", "asal": "Afrika", "tanggal_lahir": "2020-01-01", "status": "Sehat"},
    ]

    context = {
        "role": "penjaga hewan",
        "habitat": habitat,
        "hewan_list": hewan_list
    }
    return render(request, 'detail_habitat.html', context)


def create_habitat(request):
    context = {
        "role": "penjaga hewan"
    }
    return render(request, 'create_habitat.html', context)

def edit_habitat(request, id):
    context = {
        "role": "penjaga hewan"
    }
    return render(request, 'edit_habitat.html', context)