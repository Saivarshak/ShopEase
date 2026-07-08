import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopease.settings')
django.setup()

from store.models import Product

# Mark first 8 active products as featured
products = Product.objects.filter(is_active=True)[:8]
count = 0
for p in products:
    p.is_featured = True
    p.save()
    count += 1

print(f"Successfully marked {count} products as featured.")
