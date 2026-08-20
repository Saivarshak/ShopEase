from django.core.management.base import BaseCommand
from django.utils.text import slugify
from store.models import Category, FashionCategory


MENS_GALLERY = [
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


class Command(BaseCommand):
    help = "Synchronize the 16 Men's Gallery categories in exact order."

    def handle(self, *args, **options):
        mens_category = Category.objects.filter(category_name__iexact="Mens").first()
        if not mens_category:
            self.stdout.write(self.style.ERROR("Mens category not found."))
            return

        mens_root = FashionCategory.objects.filter(
            root_category=mens_category,
            parent__isnull=True,
            name__iexact="Mens",
        ).first() or FashionCategory.objects.filter(
            root_category=mens_category,
            parent__isnull=True,
        ).first()

        if not mens_root:
            self.stdout.write(self.style.ERROR("Mens root FashionCategory not found."))
            return

        self.stdout.write(
            self.style.SUCCESS(
                f"Men's root found: ID {mens_root.pk} | {mens_root.name}"
            )
        )

        existing_children = list(mens_root.children.all())
        existing_map = {c.name.strip().lower(): c for c in existing_children}
        processed_ids = set()

        for name, sort_order, image, under_maint in MENS_GALLERY:
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
                self.stdout.write(f"UPDATED | {sort_order:02d} | {obj.name} | ID {obj.pk}")
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
                    is_under_maintenance=under_maint,
                )
                processed_ids.add(obj.fashion_category_id)
                self.stdout.write(f"CREATED | {sort_order:02d} | {obj.name} | ID {obj.pk}")

        for child in existing_children:
            if child.fashion_category_id not in processed_ids:
                self.stdout.write(f"DELETING OBSOLETE | {child.name} (ID {child.pk})")
                child.delete()

        self.stdout.write(
            self.style.SUCCESS(
                f"Men's Gallery sync complete: {len(MENS_GALLERY)} cards"
            )
        )
