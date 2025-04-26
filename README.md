# SIZOPI (Sistem Informasi Zoo Pintar)

## 📋 Daftar Fitur dan Kontributor

| Warna Fitur | Nama Fitur   | Dikerjakan Oleh                         |
|-------------|--------------|----------------------------------------|
| Putih       | Fitur Putih  | Rafie Asadel Tarigan                   |
| Kuning      | Fitur Kuning | Rafie Asadel Tarigan                   |
| Hijau       | Fitur Hijau  | Ananda Joy Pratiwi Pasha Patoding     |
| Biru        | Fitur Biru   | Muhammad Fadhil Nur Aziz              |
| Merah       | Fitur Merah  | Khoirul Azmi                          |

## 🚀 Getting Started

### ⚠️ Important Notes

> 🔁 **Use `python3` instead of `python`** on Unix-based systems (Mac/Linux).  
> 💻 **Use `source env/bin/activate`** instead of `env\Scripts\activate` on Mac/Linux.  
> 📦 *The `insert_function` command requires `.env` to be included beforehand.*

---

### Set Up Environment
```bash
python -m venv env               
env/Scripts/activate               
pip install -r requirements.txt
```

### Set Up DataBase
```bash
python manage.py reset_schema
python manage.py create_table
python manage.py insert_data
python manage.py insert_fucntion
```

### Run Development Server
```bash
python manage.py runserver
```
