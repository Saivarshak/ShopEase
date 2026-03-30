from django.conf import settings
from django.db import models

class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=100, unique=True)
    image = models.CharField(max_length=255, blank=True, null=True)  # matches dump

    class Meta:
        db_table = "categories"

    def __str__(self):
        return self.category_name


class SubCategory(models.Model):
    subcategory_id = models.AutoField(primary_key=True)
    subcategory_name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        db_table = "subcategories"

    def __str__(self):
        return self.subcategory_name


class MenCategory(models.Model):
    men_category_id = models.AutoField(primary_key=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, db_column='category_id')
    category_name = models.CharField(max_length=100)
    image = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    page_url = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "men_categories"
        managed = False

    def __str__(self):
        return self.category_name


class WomenCategory(models.Model):
    women_category_id = models.AutoField(primary_key=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, db_column='category_id')
    category_name = models.CharField(max_length=100)
    image = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    page_url = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "women_categories"
        managed = False

    def __str__(self):
        return self.category_name


class KidsCategory(models.Model):
    kids_category_id = models.AutoField(primary_key=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, db_column='category_id')
    category_name = models.CharField(max_length=100)
    image = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    page_url = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "kids_categories"
        managed = False

    def __str__(self):
        return self.category_name


class SiteAsset(models.Model):
    asset_id = models.AutoField(primary_key=True)
    asset_key = models.CharField(max_length=100, unique=True)
    image_path = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "site_assets"
        managed = False

    def __str__(self):
        return self.asset_key


class PageAsset(models.Model):
    page_asset_id = models.AutoField(primary_key=True)
    page_key = models.CharField(max_length=100)
    asset_key = models.CharField(max_length=100)
    image_path = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "page_assets"
        managed = False

    def __str__(self):
        return f"{self.page_key}:{self.asset_key}"


class HomeContent(models.Model):
    home_content_id = models.AutoField(primary_key=True)
    hero_subtitle = models.CharField(max_length=255, blank=True, null=True)
    hero_title = models.CharField(max_length=255, blank=True, null=True)
    hero_highlight = models.CharField(max_length=255, blank=True, null=True)
    hero_tagline = models.CharField(max_length=255, blank=True, null=True)
    hero_button_text = models.CharField(max_length=100, blank=True, null=True)
    hero_button_url = models.CharField(max_length=255, blank=True, null=True)
    search_placeholder = models.CharField(max_length=255, blank=True, null=True)
    search_button_text = models.CharField(max_length=100, blank=True, null=True)
    nav_home_text = models.CharField(max_length=100, blank=True, null=True)
    nav_home_url = models.CharField(max_length=255, blank=True, null=True)
    nav_products_text = models.CharField(max_length=100, blank=True, null=True)
    nav_products_url = models.CharField(max_length=255, blank=True, null=True)
    nav_contact_text = models.CharField(max_length=100, blank=True, null=True)
    nav_contact_url = models.CharField(max_length=255, blank=True, null=True)
    nav_login_text = models.CharField(max_length=100, blank=True, null=True)
    nav_login_url = models.CharField(max_length=255, blank=True, null=True)
    category_section_title = models.CharField(max_length=255, blank=True, null=True)
    men_description = models.CharField(max_length=255, blank=True, null=True)
    women_description = models.CharField(max_length=255, blank=True, null=True)
    kids_description = models.CharField(max_length=255, blank=True, null=True)
    featured_section_title = models.CharField(max_length=255, blank=True, null=True)
    footer_text = models.CharField(max_length=255, blank=True, null=True)
    footer_brand_text = models.CharField(max_length=100, blank=True, null=True)
    footer_builder_text = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "home_content"
        managed = False

    def __str__(self):
        return self.hero_title or "Home Content"


class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=255)
    brand = models.CharField(max_length=100, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    sku = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    offer_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        editable=False
    )  # will compute in save()
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "products"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return self.product_name


class ProductVariant(models.Model):
    variant_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.CharField(max_length=10, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    quantity = models.IntegerField(default=0)
    image1 = models.CharField(max_length=255, blank=True, null=True)
    image2 = models.CharField(max_length=255, blank=True, null=True)
    image3 = models.CharField(max_length=255, blank=True, null=True)
    image4 = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = "product_variants"

    def __str__(self):
        return f"{self.product.product_name} - {self.size} - {self.color}"


class CartItem(models.Model):
    cart_item_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    selected_size = models.CharField(max_length=50, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "cart_items"
        unique_together = ("user", "product", "selected_size")

    def __str__(self):
        return f"{self.user} - {self.product} x {self.quantity}"


class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='India')
    payment_method = models.CharField(max_length=50, default='Card')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_items = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=50, default='Placed')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "orders"
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.order_id} - {self.user}"


class OrderItem(models.Model):
    order_item_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    selected_size = models.CharField(max_length=50, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    line_total = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "order_items"

    def __str__(self):
        return f"Order {self.order_id} - {self.product}"
