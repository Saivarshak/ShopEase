from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from django.conf import settings
from django.db import models
from django.utils.text import slugify


def _calculate_offer_price(price, discount_percent):
    try:
        normalized_price = Decimal(price or 0)
    except (InvalidOperation, TypeError):
        normalized_price = Decimal('0')

    try:
        normalized_discount = Decimal(discount_percent or 0)
    except (InvalidOperation, TypeError):
        normalized_discount = Decimal('0')

    discounted_price = normalized_price - ((normalized_price * normalized_discount) / Decimal('100'))
    return max(discounted_price, Decimal('0')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

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


class FashionCategory(models.Model):
    fashion_category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=160)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='children',
    )
    root_category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='fashion_categories',
    )
    level = models.PositiveSmallIntegerField(default=0)
    sort_order = models.PositiveIntegerField(default=0)
    image = models.CharField(max_length=255, blank=True, null=True)
    banner_image = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    page_url = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_under_maintenance = models.BooleanField(default=False)

    class Meta:
        db_table = "fashion_categories"
        ordering = ['root_category__category_name', 'level', 'sort_order', 'name']
        constraints = [
            models.UniqueConstraint(
                fields=['parent', 'slug'],
                name='unique_fashion_category_parent_slug',
            ),
        ]

    @property
    def full_path(self):
        names = [self.name]
        parent = self.parent
        while parent:
            names.append(parent.name)
            parent = parent.parent
        return " > ".join(reversed(names))

    def __str__(self):
        return self.full_path


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
    slug = models.SlugField(max_length=180, unique=True, blank=True, null=True)
    brand = models.CharField(max_length=100, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    fashion_category = models.ForeignKey(
        FashionCategory,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='products',
    )
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
        if not self.slug:
            base_slug = slugify(self.product_name)[:160] or 'product'
            slug = base_slug
            counter = 2
            while Product.objects.filter(slug=slug).exclude(product_id=self.product_id).exists():
                suffix = f'-{counter}'
                slug = f'{base_slug[:180 - len(suffix)]}{suffix}'
                counter += 1
            self.slug = slug
        self.offer_price = _calculate_offer_price(self.price, self.discount_percent)
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


class WishlistItem(models.Model):
    wishlist_item_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlist_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlist_items')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "wishlist_items"
        unique_together = ("user", "product")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.product}"


class UserAddress(models.Model):
    address_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='addresses')
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='India')
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_addresses"
        ordering = ['-is_default', '-updated_at']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_default:
            UserAddress.objects.filter(user=self.user, is_default=True).exclude(address_id=self.address_id).update(is_default=False)

    def __str__(self):
        return f"{self.full_name} - {self.city}"


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
    payment_status = models.CharField(max_length=50, default='Pending')
    currency = models.CharField(max_length=10, default='INR')
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_items = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=50, default='Placed')
    tracking_number = models.CharField(max_length=120, blank=True, null=True)
    courier_name = models.CharField(max_length=120, blank=True, null=True)
    tracking_url = models.URLField(max_length=500, blank=True, null=True)
    estimated_delivery = models.DateField(blank=True, null=True)
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
