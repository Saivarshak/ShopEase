
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopease.settings')
django.setup()

from store.models import MenCategory, WomenCategory, KidsCategory, FashionCategory

print("--- Men Categories ---")
for c in MenCategory.objects.all():
    print(f"{c.category_name} (Active: {c.is_active})")

print("\n--- Women Categories ---")
for c in WomenCategory.objects.all():
    print(f"{c.category_name} (Active: {c.is_active})")

print("\n--- Kids Categories ---")
for c in KidsCategory.objects.all():
    print(f"{c.category_name} (Active: {c.is_active})")

print("\n--- Fashion Categories (Accessories) ---")
for fc in FashionCategory.objects.filter(name__icontains='accessories'):
    print(f"ID: {fc.fashion_category_id} | Name: {fc.name} | Maintenance: {fc.is_under_maintenance}")
