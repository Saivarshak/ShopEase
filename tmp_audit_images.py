import os
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopease.settings')
import django
django.setup()

from django.conf import settings
from store.models import Product, ProductVariant, Category, SubCategory, SiteAsset, PageAsset, UploadedImage

print('BASE_DIR=', settings.BASE_DIR)
print('STATIC=', settings.BASE_DIR / 'static')
print('MEDIA=', settings.MEDIA_ROOT)
print('\nPRODUCTS')
for product in Product.objects.select_related('category', 'subcategory').order_by('product_id'):
    variants = list(ProductVariant.objects.filter(product=product).order_by('variant_id'))
    print(f'PRODUCT {product.product_id}|{product.product_name}|category={product.category.category_name}|subcategory={product.subcategory.subcategory_name}|variants={len(variants)}')
    for variant in variants:
        print(f'  VARIANT {variant.variant_id}|size={variant.size}|color={variant.color}|images={[variant.image1, variant.image2, variant.image3, variant.image4]}')
print('\nCATEGORIES')
for model, label in ((Category, 'Category'), (SubCategory, 'SubCategory')):
    for row in model.objects.all():
        print(label, row.pk, str(row), getattr(row, 'image', None))
print('\nSITE_ASSETS')
for row in SiteAsset.objects.all().order_by('asset_key'):
    print(row.asset_key, row.image_path, row.is_active)
print('\nPAGE_ASSETS')
for row in PageAsset.objects.all().order_by('page_key', 'asset_key'):
    print(row.page_key, row.asset_key, row.image_path, row.is_active)
print('\nUPLOADED_IMAGES')
for row in UploadedImage.objects.all().order_by('uploaded_image_id'):
    print(row.uploaded_image_id, row.path, row.original_name, row.content_type, row.size)
print('\nSTATIC_IMAGES')
for path in sorted((settings.BASE_DIR / 'static').rglob('*')):
    if path.is_file() and path.suffix.lower() in {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.svg', '.avif'}:
        print(path.relative_to(settings.BASE_DIR / 'static').as_posix())
