from django.contrib import admin
from .models import Category, SubCategory, Product, ProductVariant, SiteAsset, PageAsset, FashionCategory, WishlistItem, UserAddress, Order, OrderItem, UploadedImage

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
    list_display = ('product_id', 'product_name', 'slug', 'brand', 'category', 'subcategory', 'fashion_category', 'price', 'discount_percent', 'offer_price', 'is_active', 'is_featured')
    list_filter = ('category', 'subcategory', 'fashion_category', 'is_active', 'is_featured')
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


@admin.register(FashionCategory)
class FashionCategoryAdmin(admin.ModelAdmin):
    list_display = ('fashion_category_id', 'name', 'parent', 'root_category', 'level', 'sort_order', 'is_under_maintenance', 'is_active')
    list_filter = ('root_category', 'is_under_maintenance', 'is_active')
    search_fields = ('name', 'slug', 'description', 'page_url', 'banner_image')



@admin.register(UploadedImage)
class UploadedImageAdmin(admin.ModelAdmin):
    list_display = ('uploaded_image_id', 'path', 'original_name', 'content_type', 'size', 'created_at')
    search_fields = ('path', 'original_name', 'content_type')
    readonly_fields = ('path', 'original_name', 'content_type', 'size', 'created_at')
@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ('wishlist_item_id', 'user', 'product', 'created_at')
    search_fields = ('user__email', 'product__product_name')


@admin.register(UserAddress)
class UserAddressAdmin(admin.ModelAdmin):
    list_display = ('address_id', 'user', 'full_name', 'city', 'state', 'pincode', 'is_default')
    list_filter = ('country', 'state', 'is_default')
    search_fields = ('user__email', 'full_name', 'phone_number', 'city', 'pincode')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'selected_size', 'quantity', 'unit_price', 'line_total')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'user', 'subtotal', 'total_items', 'status', 'payment_status', 'tracking_number', 'created_at')
    list_filter = ('status', 'payment_status', 'payment_method', 'created_at')
    search_fields = ('order_id', 'user__email', 'full_name', 'phone_number', 'tracking_number')
    inlines = [OrderItemInline]
    
    
    
