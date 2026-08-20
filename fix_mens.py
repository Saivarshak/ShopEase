import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopease.settings')
django.setup()

from store.models import Category, FashionCategory
from django.utils.text import slugify

def fix_mens_categories():
    mens_category = Category.objects.filter(category_name__iexact='mens').first()
    if not mens_category:
        print("Mens category not found in Category table.")
        return

    mens_root = FashionCategory.objects.filter(root_category=mens_category, parent__isnull=True, name__iexact='mens').first()
    if not mens_root:
        mens_root = FashionCategory.objects.filter(root_category=mens_category, parent__isnull=True).first()
    if not mens_root:
        print("Mens root FashionCategory not found.")
        return

    exact_mens_list = [
        ("Casual Wear", 1, "images/mens_shirts.png", False),
        ("Formal Wear", 2, "images/shirt.jpg", False),
        ("Wedding Wear", 3, "images/ethicwearebg.jpeg", False),
        ("Ethnic Wear", 4, "images/ethicwearebg.jpeg", False),
        ("Party Wear", 5, "images/mens.jpg", False),
        ("Traditional Wear", 6, "images/traditional-wear.jpg", False),
        ("Suits & Blazers", 7, "images/zara-blazers.jpg", False),
        ("Denim Wear", 8, "images/wrangler-jeans.jpg", False),
        ("Streetwear", 9, "images/mens_tshirts.png", False),
        ("Activewear", 10, "images/activewear.jpg", False),
        ("Winter Wear", 11, "images/winter-wear.jpg", False),
        ("Sportswear", 12, "images/mens_tshirts.png", False),
        ("Pants & Trousers", 13, "images/zara-dress-trousers.jpg", False),
        ("Innerwear", 14, "images/mens.jpg", False),
        ("Footwear", 15, "images/mens_shoes.png", False),
        ("Accessories", 16, "images/mens_accessories.png", True),
    ]

    existing_children = list(mens_root.children.all())
    existing_map = {c.name.strip().lower(): c for c in existing_children}

    processed_ids = set()

    for name, sort_order, image, under_maint in exact_mens_list:
        key = name.strip().lower()
        if key in existing_map:
            obj = existing_map[key]
            obj.name = name
            obj.slug = slugify(name)
            obj.sort_order = sort_order
            obj.level = 1
            obj.parent = mens_root
            obj.root_category = mens_category
            if not obj.image:
                obj.image = image
            obj.description = f"Explore {name.lower()} styles and essentials."
            obj.page_url = f"/mens/{slugify(name)}/"
            obj.is_active = True
            obj.is_under_maintenance = under_maint
            obj.save()
            processed_ids.add(obj.fashion_category_id)
            print(f"UPDATED: {sort_order} - {name} (ID: {obj.fashion_category_id})")
        else:
            obj = FashionCategory.objects.create(
                name=name,
                slug=slugify(name),
                root_category=mens_category,
                parent=mens_root,
                level=1,
                sort_order=sort_order,
                image=image,
                description=f"Explore {name.lower()} styles and essentials.",
                page_url=f"/mens/{slugify(name)}/",
                is_active=True,
                is_under_maintenance=under_maint
            )
            processed_ids.add(obj.fashion_category_id)
            print(f"CREATED: {sort_order} - {name} (ID: {obj.fashion_category_id})")

    for child in existing_children:
        if child.fashion_category_id not in processed_ids:
            print(f"DELETING OBSOLETE CHILD: {child.name} (ID: {child.fashion_category_id})")
            child.delete()

    print("Men's categories successfully cleaned and synchronized!")

if __name__ == '__main__':
    fix_mens_categories()
