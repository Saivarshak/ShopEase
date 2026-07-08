import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopease.settings')
django.setup()

with connection.cursor() as cursor:
    try:
        cursor.execute("ALTER TABLE products ADD COLUMN is_featured BOOLEAN DEFAULT 0")
        print("Added is_featured column to products table.")
    except Exception as e:
        print(f"is_featured column might already exist: {e}")
        
    try:
        cursor.execute("ALTER TABLE products ADD COLUMN rating DECIMAL(3,1) DEFAULT 4.5")
        print("Added rating column to products table.")
    except Exception as e:
        print(f"rating column might already exist: {e}")
