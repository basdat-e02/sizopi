# SIZOPI

### Set Up Environment
```bash
python -m venv env
env/scripts/activate
pip install -r requirements.txt
```

### Set Up DataBase
```bash
python manage.py reset_schema
python manage.py create_table
python manage.py insert_data
python manage.py insert_fucntion
```
*insert function can be done when .env is included

### Run Development Server
```bash
python manage.py runserver
```
