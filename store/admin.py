from django.contrib import admin
from .models import Category, SubCategory, Product, ProductVariant, SiteAsset, PageAsset

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_id', 'category_name')
    search_fields = ('category_name',)

@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('subcategory_id', 'subcategory_name', 'category')
    list_filter = ('category',)
    search_fields = ('subcategory_name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_id', 'product_name', 'brand', 'category', 'subcategory', 'price', 'discount_percent', 'offer_price', 'is_active')
    list_filter = ('category', 'subcategory', 'is_active')
    search_fields = ('product_name', 'brand', 'sku')

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('variant_id', 'product', 'size', 'color', 'quantity')
    list_filter = ('product', 'size', 'color')
    search_fields = ('product__product_name',)


@admin.register(SiteAsset)
class SiteAssetAdmin(admin.ModelAdmin):
    list_display = ('asset_key', 'image_path', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('asset_key', 'image_path')


@admin.register(PageAsset)
class PageAssetAdmin(admin.ModelAdmin):
    list_display = ('page_key', 'asset_key', 'image_path', 'is_active')
    list_filter = ('page_key', 'asset_key', 'is_active')
    search_fields = ('page_key', 'asset_key', 'image_path')
    
    
    
