import os
import django
from django.utils.text import slugify

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopease.settings')
django.setup()

from store.models import Category, FashionCategory

def restore():
    # Ensure root categories exist
    men_root, _ = Category.objects.get_or_create(category_name='Men')
    women_root, _ = Category.objects.get_or_create(category_name='Women')
    kids_root, _ = Category.objects.get_or_create(category_name='Kids')

    structure = {
        'Men': {
            'root': men_root,
            'sub': ['Casual Wear', 'T-Shirts', 'Shirts', 'Jeans', 'Hoodies', 'Jackets']
        },
        'Women': {
            'root': women_root,
            'sub': ['Casual Wear', 'Tops', 'Dresses', 'Jeans', 'Kurtis', 'Ethnic Wear']
        },
        'Kids': {
            'root': kids_root,
            'sub': ['Casual Wear', 'Polo Shirts', 'T-Shirts', 'Shorts', 'Dresses', 'School Wear']
        }
    }

    for gender, data in structure.items():
        root_cat = data['root']
        for sub_name in data['sub']:
            # Create top-level fashion category for the gender
            gender_cat, _ = FashionCategory.objects.get_or_create(
                name=gender,
                slug=gender.lower(),
                parent=None,
                root_category=root_cat,
                level=0
            )
            
            # Create the sub-category
            FashionCategory.objects.get_or_create(
                name=sub_name,
                slug=slugify(sub_name),
                parent=gender_cat,
                root_category=root_cat,
                level=1
            )
            
    print("Category hierarchy restored.")

if __name__ == '__main__':
    restore()
