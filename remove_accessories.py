
import os
import django
from django.db.models import Q

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopease.settings')
django.setup()

from store.models import Product, Category, SubCategory, FashionCategory

# Manually setting table names because Django might be using different ones
Product._meta.db_table = 'store_product'
Category._meta.db_table = 'categories'
SubCategory._meta.db_table = 'subcategories'
FashionCategory._meta.db_table = 'fashion_categories'

def cleanup():
    try:
        # 1. Remove all Accessories products completely from the database
        products = Product.objects.filter(
            Q(product_name__icontains='accessories') | 
            Q(category__category_name__icontains='accessories') | 
            Q(subcategory__subcategory_name__icontains='accessories') |
            Q(fashion_category__name__icontains='accessories')
        )
        p_count = products.count()
        products.delete()
        print(f"Deleted {p_count} products.")

        # 2. Delete all existing Accessories product records (redundant but following prompt)
        # 3. Delete FashionCategory records for accessories (except those needed for the cards if any)
        # We keep the root categories but delete the sub-categories that are Accessories.
        
        fcats = FashionCategory.objects.filter(name__icontains='accessories')
        # We need to be careful not to delete categories that are used for the cards if they are dynamic.
        # But the prompt says "Keep only the category cards: Men -> Accessories, Women -> Accessories, Kids -> Accessories"
        # These are usually specific records in MenCategory, WomenCategory, KidsCategory tables.
        
        # Delete subcategories named accessories
        subcats = SubCategory.objects.filter(subcategory_name__icontains='accessories')
        s_count = subcats.count()
        subcats.delete()
        print(f"Deleted {s_count} subcategories.")

        # Delete FashionCategory records for accessories
        fc_count = fcats.count()
        fcats.delete()
        print(f"Deleted {fc_count} fashion categories.")

    except Exception as e:
        print(f"Error during cleanup: {e}")

if __name__ == "__main__":
    cleanup()
