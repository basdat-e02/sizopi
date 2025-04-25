from django.db import connection
import os
from django.conf import settings
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Run raw SQL from insert_data.sql'

    def handle(self, *args, **options):

        sql_path = os.path.join(settings.SQL_DIR, 'satwa_habitat.sql')

        if not os.path.exists(sql_path):
            self.stdout.write(self.style.ERROR(f"SQL file not found at {sql_path}"))
            return

        self.stdout.write(self.style.SUCCESS(f"Running SQL file from: {sql_path}"))

        with open(sql_path, 'r', encoding='utf-8') as f:
            sql = f.read()

        try:
            with connection.cursor() as cursor:
                if 'sqlite3' in connection.settings_dict['ENGINE']:
                    self.stdout.write(self.style.ERROR(f"❌ SQLite3 doesn't support stored procedures or custom functions"))
                else:
                    for statement in sql.split(';'):
                        if statement.strip():
                            cursor.execute(statement)  # for PostgreSQL or others
                    self.stdout.write(self.style.SUCCESS("✅ Successfully ran insert_data.sql"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error executing SQL: {e}"))