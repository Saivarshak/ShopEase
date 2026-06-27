
import os
import django
from django.db.models import Q

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopease.settings')
django.setup()

from store.models import Product, Category, SubCategory, MenCategory, WomenCategory, KidsCategory, FashionCategory

def cleanup():
    try:
        # 1. Remove all Accessories products completely from the database
        products = Product.objects.filter(
            Q(product_name__icontains='accessories') | 
            Q(category__category_name__icontains='accessories') | 
            Q(subcategory__subcategory_name__icontains='accessories')
        )
        p_count = products.count()
        products.delete()
        print(f"Deleted {p_count} products.")

        # 2. Remove Accessories categories and subcategories records
        # Note: We keep the category cards visible for navigation later by logic, 
        # but the requirement says "Remove all Accessories products completely from the database and delete all existing Accessories product records."
        # And "Remove the Accessories section/cards from the Home Page".
        # We also need to "Keep only the category cards: Men -> Accessories, Women -> Accessories, Kids -> Accessories" 
        # but redirect them to Under Maintenance.
        
        # If we delete the category records, the cards might disappear if they are dynamic.
        # The home view uses MenCategory, WomenCategory, KidsCategory for cards.
        
        # Let's delete SubCategory records named 'accessories'
        subcats = SubCategory.objects.filter(subcategory_name__icontains='accessories')
        s_count = subcats.count()
        subcats.delete()
        print(f"Deleted {s_count} subcategories.")

        # We should NOT delete MenCategory/WomenCategory/KidsCategory records for Accessories 
        # if we want to keep the cards visible but redirecting.
        # Requirement 3 says: "Keep only the category cards: Men -> Accessories, Women -> Accessories, Kids -> Accessories"
        
        # Requirement 6: "Ensure Accessories products cannot be accessed through direct URLs, search results, category pages, featured products, related products, API endpoints, or admin product listings."
        # Deleting the products handles most of this.
        
        # Deleting FashionCategory records for accessories
        fcats = FashionCategory.objects.filter(name__icontains='accessories')
        fc_count = fcats.count()
        fcats.delete()
        print(f"Deleted {fc_count} fashion categories.")

    except Exception as e:
        print(f"Error during cleanup: {e}")

if __name__ == "__main__":
    cleanup()
