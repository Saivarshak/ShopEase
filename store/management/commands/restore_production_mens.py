from django.core.management.base import BaseCommand
from store.models import FashionCategory
import json
import os

class Command(BaseCommand):
    help = 'Restores and synchronizes all missing Men Wear category cards and subcategories from mens_gallery.json'

    def handle(self, *args, **options):
        self.stdout.write("Starting production Men's Wear restoration...")

        json_path = os.path.join('data', 'mens_gallery.json')
        if not os.path.exists(json_path):
            self.stdout.write(self.style.ERROR(f"Could not find {json_path}"))
            return

        with open(json_path, 'r', encoding='utf-8') as f:
            items = json.load(f)

        # Find Men category
        men_cat = FashionCategory.objects.filter(name__iexact='Men').first() or FashionCategory.objects.filter(name__iexact='Mens').first()
        if not men_cat:
            self.stdout.write(self.style.ERROR("Men category not found in database!"))
            return

        self.stdout.write(f"Found parent Men category ID: {men_cat.fashion_category_id}")

        updated_count = 0
        for item in items:
            fields = item.get('fields', {})
            name = fields.get('name')
            slug = fields.get('slug')
            sort_order = fields.get('sort_order', 1)
            description = fields.get('description', '')
            image = fields.get('image', '')
            page_url = fields.get('page_url', '')
            is_active = fields.get('is_active', True)
            is_under_maintenance = fields.get('is_under_maintenance', False)

            cat, created = FashionCategory.objects.update_or_create(
                parent=men_cat,
                slug=slug,
                defaults={
                    'name': name,
                    'level': 1,
                    'sort_order': sort_order,
                    'is_active': is_active,
                    'is_under_maintenance': is_under_maintenance,
                    'root_category_id': 5, # Standard root for fashion
                    'description': description,
                    'image': image,
                    'page_url': page_url,
                }
            )
            updated_count += 1
            action = "Created" if created else "Updated"
            self.stdout.write(f"{action} Men card: {name} (Slug: {slug})")

        total_cards = FashionCategory.objects.filter(parent=men_cat).count()
        self.stdout.write(self.style.SUCCESS(f"Successfully synchronized {updated_count} Men's Wear cards. Total cards under Men: {total_cards}"))
