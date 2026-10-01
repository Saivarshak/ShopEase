import os
from collections import defaultdict
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopease.settings')
import django
django.setup()
from django.apps import apps
from django.db import connection
from store.models import Category, SubCategory, Product, FashionCategory

print('CATEGORY_FK_FIELDS:')
for model in apps.get_models():
    for field in model._meta.get_fields():
        if getattr(field, 'remote_field', None) and getattr(field.remote_field, 'model', None) is Category:
            print(model._meta.label, field.name, field.remote_field.on_delete.__name__)
            for cat in Category.objects.order_by('category_id'):
                try:
                    print(' ', cat.category_id, cat.category_name, model._default_manager.filter(**{field.name: cat}).count())
                except Exception as exc: print(' ', cat.category_id, 'ERROR', exc)

print('SUBCATEGORY_ROWS_BY_ROOT:')
for cat in Category.objects.order_by('category_id'):
    print('ROOT', cat.category_id, cat.category_name)
    for s in SubCategory.objects.filter(category=cat).order_by('subcategory_id'):
        print(' ', s.subcategory_id, repr(s.subcategory_name), 'products=', Product.objects.filter(subcategory=s).count())

print('FASHION_TREE_BY_ROOT:')
for cat in Category.objects.order_by('category_id'):
    print('ROOT', cat.category_id, cat.category_name)
    rows = FashionCategory.objects.filter(root_category=cat).order_by('level','sort_order','fashion_category_id')
    for f in rows:
        print(' ', f.fashion_category_id, repr(f.name), f.slug, 'parent=', f.parent_id, 'level=', f.level, 'active=', f.is_active, 'maintenance=', f.is_under_maintenance, 'products=', Product.objects.filter(fashion_category=f).count())

print('DUPLICATE_SUBCATEGORY_NAMES_BY_CANONICAL_ROOT:')
for canonical_id, duplicate_id in [(5,1),(6,2),(7,3)]:
    canon = defaultdict(list); dup = defaultdict(list)
    for s in SubCategory.objects.filter(category_id=canonical_id): canon[s.subcategory_name.casefold()].append(s)
    for s in SubCategory.objects.filter(category_id=duplicate_id): dup[s.subcategory_name.casefold()].append(s)
    print('PAIR', duplicate_id, 'TO', canonical_id)
    for key in sorted(set(canon)|set(dup)):
        print(' ', key, 'canonical_ids=', [s.subcategory_id for s in canon.get(key,[])], 'duplicate_ids=', [s.subcategory_id for s in dup.get(key,[])])
print('DONE')
