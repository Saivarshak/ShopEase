import os
from collections import defaultdict
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopease.settings')
import django
django.setup()
from django.conf import settings
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from store.models import Category, SubCategory, Product, FashionCategory, MenCategory, WomenCategory, KidsCategory, UploadedImage, ProductVariant
from django.contrib.auth import get_user_model
print('ENGINE:', connection.vendor)
print('DATABASES_DEFAULT_ENGINE:', settings.DATABASES['default'].get('ENGINE'))
print('DATABASES_DEFAULT_NAME:', settings.DATABASES['default'].get('NAME'))
print('DATABASE_URL_PRESENT:', bool(os.environ.get('DATABASE_URL', '').strip()))
print('DB_TABLES:', ', '.join(sorted(connection.introspection.table_names())))
executor = MigrationExecutor(connection)
plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
print('PENDING_MIGRATIONS:', len(plan))
for migration, backwards in plan: print('PENDING:', migration.app_label, migration.name)
for label, model in [('Category', Category), ('SubCategory', SubCategory), ('FashionCategory', FashionCategory), ('Product', Product), ('ProductVariant', ProductVariant), ('UploadedImage', UploadedImage), ('User', get_user_model())]:
    try: print(f'{label}: {model.objects.count()}')
    except Exception as exc: print(f'{label}: ERROR {exc}')
print('CATEGORY_ROWS:')
for row in Category.objects.order_by('category_name', 'category_id').values('category_id', 'category_name', 'image'):
    cid = row['category_id']
    print(row, 'subcategories=', SubCategory.objects.filter(category_id=cid).count(), 'products=', Product.objects.filter(category_id=cid).count(), 'fashion_categories=', FashionCategory.objects.filter(root_category_id=cid).count(), 'men_rows=', MenCategory.objects.filter(category_id=cid).count(), 'women_rows=', WomenCategory.objects.filter(category_id=cid).count(), 'kids_rows=', KidsCategory.objects.filter(category_id=cid).count())
print('CASE_INSENSITIVE_DUPLICATES:')
by_name = defaultdict(list)
for row in Category.objects.order_by('category_name', 'category_id').values('category_id', 'category_name'):
    by_name[row['category_name'].casefold()].append(row)
for key, rows in by_name.items():
    if len(rows) > 1: print(key, rows)
print('FASHION_ROOTS:')
for row in FashionCategory.objects.filter(parent__isnull=True).select_related('root_category').order_by('root_category__category_name', 'sort_order', 'fashion_category_id'):
    print(row.fashion_category_id, row.name, row.slug, 'root_id=', row.root_category_id, 'root_name=', row.root_category.category_name if row.root_category else None, 'active=', row.is_active, 'maintenance=', row.is_under_maintenance)
print('PRODUCT_CATEGORY_MISMATCHES:')
for p in Product.objects.select_related('category', 'subcategory', 'fashion_category').order_by('product_id'):
    if p.subcategory_id and p.subcategory.category_id != p.category_id: print('subcategory_category_mismatch', p.product_id, p.product_name, p.category_id, p.subcategory_id, p.subcategory.category_id)
    if p.fashion_category_id and p.fashion_category.root_category_id and p.fashion_category.root_category_id != p.category_id: print('fashion_root_category_mismatch', p.product_id, p.product_name, p.category_id, p.fashion_category_id, p.fashion_category.root_category_id)
print('STATIC_DIRS:', [str(p) for p in settings.STATICFILES_DIRS])
print('STATIC_ROOT:', settings.STATIC_ROOT)
print('MEDIA_ROOT:', settings.MEDIA_ROOT)
print('UPLOADED_IMAGES:', UploadedImage.objects.count())
print('DONE')
