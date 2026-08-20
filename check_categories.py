import os
import django
import sys

# Setup Django environment
sys.path.append(r'C:\Users\saiva\OneDrive\Desktop\Live project Online shoping')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopease.settings')
django.setup()

from store.models import FashionCategory

names = ["Track Pants", "Sweatshirts", "Jackets", "Tank Tops & Vests", "Lounge Wear"]
for name in names:
    print(f"--- {name} ---")
    cats = FashionCategory.objects.filter(name=name, parent_id=200)
    for cat in cats:
        print(f"ID:{cat.fashion_category_id} | Image:{cat.image} | Order:{cat.sort_order}")
