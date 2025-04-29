# SIZOPI (Sistem Informasi Zoo Pintar)

## 📋 Daftar Fitur dan Kontributor

| Warna Fitur | Dikerjakan Oleh                         |
|-------------|----------------------------------------|
| Putih       | Rafie Asadel Tarigan                   |
| Kuning      | Rafie Asadel Tarigan                   |
| Hijau       | Ananda Joy Pratiwi Pasha Patoding     |
| Biru        | Muhammad Fadhil Nur Aziz              |
| Merah       | Khoirul Azmi                          |

## 🚀 Getting Started

> ### ⚠️ Important Notes
> 
> 📄 *See `main/views.py` for additional development info.*
> 🔁 **Use `python3` instead of `python`** on Unix-based systems (Mac/Linux).  
> 💻 **Use `source env/bin/activate`** instead of `env\Scripts\activate` on Mac/Linux.  
> 📦 *The `insert_function` command requires `.env` to be included beforehand.* 


### Set Up Environment
```bash
python -m venv env               
env/Scripts/activate               
pip install -r requirements.txt
```

### Set Up DataBase
Create a `.env` file in the root directory of the project. Then copy and paste the following configuration into the `.env` file:
```.env
user=postgres.nktxoorzfzijgjshumsi 
password=sizopi123__
host=aws-0-ap-southeast-1.pooler.supabase.com
port=6543
dbname=postgres
```
After setting up the .env file, run the following commands in your terminal:
```bash
python manage.py reset_schema
python manage.py create_table
python manage.py insert_data
python manage.py insert_function
```

### Run Development Server
```bash
python manage.py runserver
```
