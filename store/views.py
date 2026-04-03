from pathlib import Path
from decimal import Decimal, InvalidOperation
import hashlib
import hmac
import time

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import connection, transaction
from django.db.utils import OperationalError, ProgrammingError
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.text import slugify
import requests
from .models import (
    Product,
    Category,
    SubCategory,
    ProductVariant,
    CartItem,
    Order,
    OrderItem,
    MenCategory,
    WomenCategory,
    KidsCategory,
    SiteAsset,
    PageAsset,
    HomeContent,
)


def _asset_exists(normalized_path):
    static_candidate = Path(settings.BASE_DIR) / 'static' / normalized_path
    if static_candidate.exists():
        return normalized_path

    image_name = Path(normalized_path).name
    static_images_candidate = Path(settings.BASE_DIR) / 'static' / 'images' / image_name
    if static_images_candidate.exists():
        return f'images/{image_name}'
    return None


def _get_site_asset(asset_key, fallback):
    try:
        asset = SiteAsset.objects.filter(asset_key=asset_key, is_active=True).first()
    except (ProgrammingError, OperationalError):
        asset = None

    if asset and asset.image_path:
        normalized = asset.image_path.replace('\\', '/').lstrip('/')
        resolved = _asset_exists(normalized)
        if resolved:
            return resolved
    return fallback


def _get_page_asset(page_key, asset_key, fallback):
    try:
        asset = PageAsset.objects.filter(page_key=page_key, asset_key=asset_key, is_active=True).first()
    except (ProgrammingError, OperationalError):
        asset = None

    if asset and asset.image_path:
        normalized = asset.image_path.replace('\\', '/').lstrip('/')
        resolved = _asset_exists(normalized)
        if resolved:
            return resolved
    return fallback


def _get_product_image_path(product, variant):
    category_name = (getattr(product.category, 'category_name', '') or '').lower()
    subcategory_name = (getattr(product.subcategory, 'subcategory_name', '') or '').lower()
    fallback_map = {
        ('mens', 't-shirts'): 'images/T-shirt.jpg',
        ('mens', 'shirts'): 'images/mens_shirts.png',
        ('mens', 'jeans'): 'images/mens_jeans.png',
        ('mens', 'accessories'): 'images/mens_accessories.png',
        ('womens', 'ethnic wear'): 'images/women-ethnic.png',
        ('womens', 'western wear'): 'images/women-western.png',
        ('womens', 'footwear'): 'images/women-footwear1.png',
        ('womens', 'bags & accessories'): 'images/women-bags.png',
        ('womens', 'bags and accessories'): 'images/women-bags.png',
        ('kids', 't-shirts'): 'images/kids-tshirts.png',
        ('kids', 'kids dresses'): 'images/kids-dresses.png',
        ('kids', 'dresses'): 'images/kids-dresses.png',
        ('kids', 'toys'): 'images/kids-toys.png',
        ('kids', 'footwear'): 'images/kids-footwear.png',
    }
    fallback_image = fallback_map.get((category_name, subcategory_name), 'images/homebg.jpg')
    image_names = [variant.image1, variant.image2, variant.image3, variant.image4] if variant else []

    for image_name in image_names:
        if not image_name:
            continue
        resolved = _asset_exists(f'images/{image_name}')
        if resolved:
            return resolved
    return fallback_image


def _get_razorpay_credentials():
    key_id = (getattr(settings, 'RAZORPAY_KEY_ID', '') or '').strip()
    key_secret = (getattr(settings, 'RAZORPAY_KEY_SECRET', '') or '').strip()
    return key_id, key_secret


def _is_razorpay_configured():
    key_id, key_secret = _get_razorpay_credentials()
    return bool(key_id and key_secret)


def _build_razorpay_receipt(user_id):
    return f"rcpt_{user_id}_{int(time.time())}"[:40]


def _create_razorpay_order(amount_paise, receipt, notes=None):
    key_id, key_secret = _get_razorpay_credentials()
    if not key_id or not key_secret:
        raise ValueError('Razorpay keys are not configured.')

    response = requests.post(
        'https://api.razorpay.com/v1/orders',
        auth=(key_id, key_secret),
        json={
            'amount': amount_paise,
            'currency': 'INR',
            'receipt': receipt,
            'notes': notes or {},
        },
        timeout=20,
    )
    response.raise_for_status()
    return response.json()


def _fetch_razorpay_payment(payment_id):
    key_id, key_secret = _get_razorpay_credentials()
    if not key_id or not key_secret:
        raise ValueError('Razorpay keys are not configured.')

    response = requests.get(
        f'https://api.razorpay.com/v1/payments/{payment_id}',
        auth=(key_id, key_secret),
        timeout=20,
    )
    response.raise_for_status()
    return response.json()


def _friendly_razorpay_error(exc):
    message = str(exc)
    lowered = message.lower()
    if 'failed to establish a new connection' in lowered or 'unable to connect to proxy' in lowered or 'max retries exceeded' in lowered:
        return 'The server could not reach Razorpay right now. Please check internet or firewall access on this machine, or use the Razorpay Link / QR payment option.'
    return message


def _verify_razorpay_signature(order_id, payment_id, signature):
    _, key_secret = _get_razorpay_credentials()
    generated_signature = hmac.new(
        key_secret.encode(),
        f'{order_id}|{payment_id}'.encode(),
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(generated_signature, signature)


def _get_category_image_path(category):
    fallback_by_category = {
        'mens': 'images/men.png',
        'men': 'images/men.png',
        'womens': 'images/women.png',
        'women': 'images/women.png',
        'kids': 'images/kids.png',
    }

    if category.image:
        normalized = category.image.replace('\\', '/').lstrip('/')
        resolved = _asset_exists(normalized)
        if resolved:
            return resolved

    return fallback_by_category.get(category.category_name.lower(), 'images/homebg.jpg')


def _resolve_static_image_path(raw_path, fallback):
    if raw_path:
        normalized = raw_path.replace('\\', '/').lstrip('/')
        resolved = _asset_exists(normalized)
        if resolved:
            return resolved
    return fallback


def _load_category_cards(queryset, fallback_map, empty_fallback):
    try:
        items = queryset
        results = []
        for item in items:
            key = (item.category_name or '').lower()
            results.append({
                'name': item.category_name,
                'image_path': _resolve_static_image_path(item.image, fallback_map.get(key, empty_fallback)),
                'description': item.description or 'Explore this category.',
                'page_url': item.page_url or '#',
            })
        return results
    except (ProgrammingError, OperationalError):
        return []


def _build_product_cards(products):
    image_cards = []

    for product in products:
        variant = ProductVariant.objects.filter(product=product).first()
        image_names = [variant.image1, variant.image2, variant.image3, variant.image4] if variant else []

        valid_images = []
        for image_name in image_names:
            if not image_name:
                continue
            resolved = _asset_exists(f'images/{image_name}')
            if resolved:
                valid_images.append(resolved)

        if not valid_images:
            valid_images = [_get_product_image_path(product, variant)]

        primary_image = valid_images[0] if valid_images else _get_product_image_path(product, variant)
        image_cards.append({
            'product_id': product.product_id,
            'product_name': product.product_name,
            'brand': product.brand,
            'offer_price': product.offer_price,
            'image_path': primary_image,
            'card_name': product.product_name,
        })

    return image_cards


def _get_session_cart(request):
    return request.session.get('cart', {})


def _set_session_cart(request, cart_data):
    request.session['cart'] = {str(product_id): int(quantity) for product_id, quantity in cart_data.items() if int(quantity) > 0}
    request.session.modified = True


def _merge_session_cart_into_db(request, user):
    session_cart = _get_session_cart(request)
    if not session_cart:
        return

    for product_id, quantity in session_cart.items():
        product = Product.objects.filter(product_id=product_id, is_active=True).first()
        if not product:
            continue

        cart_item, created = CartItem.objects.get_or_create(
            user=user,
            product=product,
            selected_size=None,
            defaults={'quantity': max(1, int(quantity))},
        )
        if not created:
            cart_item.quantity += max(1, int(quantity))
            cart_item.save(update_fields=['quantity', 'updated_at'])

    _set_session_cart(request, {})


def _get_user_cart_items(user):
    return CartItem.objects.filter(user=user, product__is_active=True).select_related('product')


def _get_effective_cart_data(request):
    if request.user.is_authenticated:
        return _get_user_cart_items(request.user)
    return _get_session_cart(request)


def _set_user_cart_item(user, product, quantity, selected_size=None, replace=False):
    quantity = max(1, int(quantity))
    if selected_size:
        matching_variant = ProductVariant.objects.filter(product=product, size__iexact=selected_size).first()
        available_stock = max(0, getattr(matching_variant, 'quantity', 0) or 0)
    else:
        available_stock = sum(ProductVariant.objects.filter(product=product).values_list('quantity', flat=True))

    if available_stock == 0:
        return False, 0

    cart_item, created = CartItem.objects.get_or_create(
        user=user,
        product=product,
        selected_size=selected_size,
        defaults={'quantity': quantity},
    )
    if not created:
        cart_item.quantity = quantity if replace else cart_item.quantity + quantity
        cart_item.quantity = min(cart_item.quantity, available_stock)
        cart_item.save(update_fields=['quantity', 'updated_at'])
    else:
        if cart_item.quantity > available_stock:
            cart_item.quantity = available_stock
            cart_item.save(update_fields=['quantity', 'updated_at'])

    return True, available_stock


def _remove_user_cart_item(user, product_id):
    CartItem.objects.filter(user=user, product_id=product_id).delete()


def _build_cart_summary(cart_data):
    cart_items = []
    subtotal = 0
    total_items = 0

    if hasattr(cart_data, 'model') and cart_data.model is CartItem:
        for item in cart_data:
            product = item.product
            variant = ProductVariant.objects.filter(
                product=product,
                size__iexact=item.selected_size,
            ).first() if item.selected_size else ProductVariant.objects.filter(product=product).first()
            line_total = product.offer_price * item.quantity
            subtotal += line_total
            total_items += item.quantity
            cart_items.append({
                'cart_item_id': item.cart_item_id,
                'product': product,
                'variant': variant,
                'selected_size': item.selected_size,
                'quantity': item.quantity,
                'image_path': _get_product_image_path(product, variant),
                'line_total': line_total,
            })
    else:
        for product_id, quantity in cart_data.items():
            product = Product.objects.filter(product_id=product_id, is_active=True).first()
            if not product:
                continue

            variant = ProductVariant.objects.filter(product=product).first()
            line_total = product.offer_price * quantity
            subtotal += line_total
            total_items += quantity
            cart_items.append({
                'product': product,
                'variant': variant,
                'selected_size': None,
                'quantity': quantity,
                'image_path': _get_product_image_path(product, variant),
                'line_total': line_total,
            })

    return cart_items, subtotal, total_items

# Home page

def home(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    featured_products = []
    categories_context = []
    home_content = None

    for product in products:
        variant = ProductVariant.objects.filter(product=product).first()
        featured_products.append({
            'product': product,
            'image_path': _get_product_image_path(product, variant),
        })

    try:
        home_content = HomeContent.objects.filter(is_active=True).first()
    except (ProgrammingError, OperationalError):
        home_content = None

    category_routes = {
        'mens': 'category_men',
        'men': 'category_men',
        'womens': 'category_women',
        'women': 'category_women',
        'kids': 'category_kids',
    }

    category_descriptions = {
        'mens': getattr(home_content, 'men_description', None) or 'Casual wear, formals, accessories and more.',
        'men': getattr(home_content, 'men_description', None) or 'Casual wear, formals, accessories and more.',
        'womens': getattr(home_content, 'women_description', None) or 'Ethnic, western, and everything chic!',
        'women': getattr(home_content, 'women_description', None) or 'Ethnic, western, and everything chic!',
        'kids': getattr(home_content, 'kids_description', None) or 'Trendy and comfy styles for kids of all ages.',
    }

    for category in categories:
        key = category.category_name.lower()
        categories_context.append({
            'name': category.category_name.title().replace('Womens', 'Women').replace('Mens', 'Men'),
            'image_path': _get_category_image_path(category),
            'route_name': category_routes.get(key, 'home'),
            'description': category_descriptions.get(key, 'Explore products in this category.'),
        })

    logo_image = _get_site_asset('logo', 'images/logo1.png')
    background_image = _get_site_asset('home_background', 'images/homebg.jpg')
    hero_banner_image = _get_site_asset('home_banner', 'images/banner.jpg')

    return render(request, 'store/home.html', {
        'products': products,
        'featured_products': featured_products,
        'categories_context': categories_context,
        'logo_image': logo_image,
        'background_image': background_image,
        'hero_banner_image': hero_banner_image,
        'hero_subtitle': getattr(home_content, 'hero_subtitle', None) or 'For Modern Shoppers',
        'hero_title': getattr(home_content, 'hero_title', None) or 'Relax,',
        'hero_highlight': getattr(home_content, 'hero_highlight', None) or 'ShopEase',
        'hero_tagline': getattr(home_content, 'hero_tagline', None) or 'Faster, Fairer, and Closer to You',
        'hero_button_text': getattr(home_content, 'hero_button_text', None) or 'Explore Products',
        'hero_button_url': getattr(home_content, 'hero_button_url', None) or '/category_men/',
        'search_placeholder': getattr(home_content, 'search_placeholder', None) or 'Search for products...',
        'search_button_text': getattr(home_content, 'search_button_text', None) or 'Search',
        'nav_home_text': getattr(home_content, 'nav_home_text', None) or 'Home',
        'nav_home_url': getattr(home_content, 'nav_home_url', None) or '/',
        'nav_products_text': getattr(home_content, 'nav_products_text', None) or 'Products',
        'nav_products_url': getattr(home_content, 'nav_products_url', None) or '#featured-products',
        'nav_contact_text': getattr(home_content, 'nav_contact_text', None) or 'Contact Us',
        'nav_contact_url': getattr(home_content, 'nav_contact_url', None) or '#',
        'nav_login_text': getattr(home_content, 'nav_login_text', None) or 'Login',
        'nav_login_url': getattr(home_content, 'nav_login_url', None) or '/login/',
        'category_section_title': getattr(home_content, 'category_section_title', None) or 'Shop by Category',
        'featured_section_title': getattr(home_content, 'featured_section_title', None) or 'Featured Products',
        'footer_text': getattr(home_content, 'footer_text', None) or 'All rights reserved.',
        'footer_brand_text': getattr(home_content, 'footer_brand_text', None) or 'ShopEase',
        'footer_builder_text': getattr(home_content, 'footer_builder_text', None) or 'MR Technologies',
        'search_query': '',
        'profile_photo_url': request.session.get('profile_photo_url', ''),
    })


def search_results(request):
    search_query = (request.GET.get('q') or '').strip()
    products = Product.objects.none()
    if search_query:
        search_tokens = [token for token in search_query.replace('-', ' ').split() if token]
        search_filter = (
            Q(product_name__icontains=search_query) |
            Q(brand__icontains=search_query) |
            Q(category__category_name__icontains=search_query) |
            Q(subcategory__subcategory_name__icontains=search_query)
        )

        for token in search_tokens:
            search_filter |= (
                Q(product_name__icontains=token) |
                Q(brand__icontains=token) |
                Q(category__category_name__icontains=token) |
                Q(subcategory__subcategory_name__icontains=token)
            )

        if 'tshirt' in search_query.lower() or 't shirt' in search_query.lower() or 't-shirt' in search_query.lower():
            search_filter |= (
                Q(product_name__icontains='t-shirt') |
                Q(product_name__icontains='t shirt') |
                Q(product_name__icontains='tshirt') |
                Q(subcategory__subcategory_name__icontains='t-shirt') |
                Q(subcategory__subcategory_name__icontains='t shirt') |
                Q(subcategory__subcategory_name__icontains='tshirt')
            )

        products = Product.objects.filter(search_filter).distinct()

    searched_products = []
    for product in products:
        variant = ProductVariant.objects.filter(product=product).first()
        searched_products.append({
            'product': product,
            'image_path': _get_product_image_path(product, variant),
        })

    try:
        home_content = HomeContent.objects.filter(is_active=True).first()
    except (ProgrammingError, OperationalError):
        home_content = None

    return render(request, 'store/search-results.html', {
        'searched_products': searched_products,
        'search_query': search_query,
        'logo_image': _get_site_asset('logo', 'images/logo1.png'),
        'search_placeholder': getattr(home_content, 'search_placeholder', None) or 'Search for products...',
        'search_button_text': getattr(home_content, 'search_button_text', None) or 'Search',
        'nav_home_text': getattr(home_content, 'nav_home_text', None) or 'Home',
        'nav_home_url': getattr(home_content, 'nav_home_url', None) or '/',
        'nav_products_text': getattr(home_content, 'nav_products_text', None) or 'Products',
        'nav_products_url': getattr(home_content, 'nav_products_url', None) or '#featured-products',
        'nav_contact_text': getattr(home_content, 'nav_contact_text', None) or 'Contact Us',
        'nav_contact_url': getattr(home_content, 'nav_contact_url', None) or '#',
        'nav_login_text': getattr(home_content, 'nav_login_text', None) or 'Login',
        'nav_login_url': getattr(home_content, 'nav_login_url', None) or '/login/',
        'footer_text': getattr(home_content, 'footer_text', None) or 'All rights reserved.',
        'footer_brand_text': getattr(home_content, 'footer_brand_text', None) or 'ShopEase',
        'footer_builder_text': getattr(home_content, 'footer_builder_text', None) or 'MR Technologies',
    })


def category_view(request, category_name):
    category_lookup = {
        'men': 'mens',
        'women': 'womens',
        'kids': 'kids',
    }
    template_lookup = {
        'mens': 'store/category-men.html',
        'womens': 'store/category-women.html',
        'kids': 'store/category-kids.html',
    }

    normalized_name = category_lookup.get(category_name.lower(), category_name.lower())
    category = get_object_or_404(Category, category_name__iexact=normalized_name)
    products = Product.objects.filter(category=category, is_active=True).select_related('category', 'subcategory')
    template_name = template_lookup.get(category.category_name.lower(), 'store/category-men.html')

    context = {'products': products, 'category': category}
    if category.category_name.lower() == 'mens':
        fallback_map = {
            't-shirts': 'images/T-shirt.jpg',
            'shirts': 'images/mens_shirts.png',
            'jeans': 'images/mens_jeans.png',
            'accessories': 'images/mens_accessories.png',
        }
        context['men_categories'] = _load_category_cards(
            MenCategory.objects.filter(category=category, is_active=True),
            fallback_map,
            'images/T-shirt.jpg',
        )
        context['page_background_image'] = _get_page_asset('category_men', 'background', 'images/bg.jpg')
    elif category.category_name.lower() == 'womens':
        fallback_map = {
            'ethnic wear': 'images/women-ethnic.png',
            'western wear': 'images/women-western.png',
            'footwear': 'images/women-footwear1.png',
            'bags & accessories': 'images/women-bags.png',
            'bags and accessories': 'images/women-bags.png',
        }
        context['women_categories'] = _load_category_cards(
            WomenCategory.objects.filter(category=category, is_active=True),
            fallback_map,
            'images/women.png',
        )
        context['page_background_image'] = _get_page_asset('category_women', 'background', 'images/bg.jpg')
    elif category.category_name.lower() == 'kids':
        fallback_map = {
            't-shirts': 'images/kids-tshirts.png',
            'kids dresses': 'images/kids-dresses.png',
            'dresses': 'images/kids-dresses.png',
            'toys': 'images/kids-toys.png',
            'footwear': 'images/kids-footwear.png',
        }
        context['kids_categories'] = _load_category_cards(
            KidsCategory.objects.filter(category=category, is_active=True),
            fallback_map,
            'images/kids.png',
        )
        context['page_background_image'] = _get_page_asset('category_kids', 'background', 'images/bg.jpg')

    context['logo_image'] = _get_site_asset('logo', 'images/logo1.png')

    return render(request, template_name, context)

def product_detail(request, product_id):
    product = get_object_or_404(Product.objects.select_related('category', 'subcategory'), product_id=product_id, is_active=True)
    variant = ProductVariant.objects.filter(product=product).first()
    fallback_image = _get_product_image_path(product, variant)
    size_variants = list(ProductVariant.objects.filter(product=product).exclude(size__isnull=True).exclude(size__exact='').order_by('variant_id'))
    return render(request, 'store/product-detail-generic.html', {
        'product': product,
        'variant': variant,
        'size_variants': size_variants,
        'total_stock': _get_total_stock(product),
        'logo_image': _get_site_asset('logo', 'images/logo1.png'),
        'detail_fallback_front': fallback_image,
        'detail_fallback_back': fallback_image,
        'detail_fallback_side': fallback_image,
        'detail_fallback_close': fallback_image,
    })


def mens_tshirts(request):
    products = Product.objects.filter(
        category__category_name__iexact='mens',
        subcategory__subcategory_name__iexact='t-shirts',
        is_active=True,
    ).select_related('category', 'subcategory')

    image_cards = []
    fallback_images = [
        _get_page_asset('mens_tshirt_detail', 'fallback_front', 'images/T-shirt.jpg'),
        _get_page_asset('mens_tshirt_detail', 'fallback_side', 'images/T-shirt side.jpg'),
        _get_page_asset('mens_tshirt_detail', 'fallback_back', 'images/T-shirt back.jpg'),
        _get_page_asset('mens_tshirt_detail', 'fallback_close', 'images/T-shirt close.jpg'),
    ]

    for product in products:
        variant = ProductVariant.objects.filter(product=product).first()
        image_names = [variant.image1, variant.image2, variant.image3, variant.image4] if variant else []

        valid_images = []
        for image_name in image_names:
            if not image_name:
                continue
            image_path = Path(settings.BASE_DIR) / 'static' / 'images' / image_name
            if image_path.exists():
                valid_images.append(f'images/{image_name}')

        if not valid_images:
            valid_images = [image_path for image_path in fallback_images if image_path]

        primary_image = valid_images[0] if valid_images else _get_product_image_path(product, variant)
        image_cards.append({
            'product_id': product.product_id,
            'product_name': product.product_name,
            'brand': product.brand,
            'offer_price': product.offer_price,
            'image_path': primary_image,
            'card_name': product.product_name,
        })

    return render(request, 'store/mens-tshirts.html', {
        'image_cards': image_cards,
        'logo_image': _get_site_asset('logo', 'images/logo1.png'),
        'page_background_image': _get_page_asset('mens_tshirts', 'background', 'images/menstshirts.jpg'),
    })


def mens_tshirt_detail(request, product_id):
    product = get_object_or_404(
        Product.objects.select_related('category', 'subcategory'),
        product_id=product_id,
        category__category_name__iexact='mens',
        subcategory__subcategory_name__iexact='t-shirts',
        is_active=True,
    )
    return redirect('catalog_product_detail', product_id=product.product_id)


def mens_jeans(request):
    products = Product.objects.filter(
        category__category_name__iexact='mens',
        subcategory__subcategory_name__iexact='jeans',
        is_active=True,
    ).select_related('category', 'subcategory')

    image_cards = []
    fallback_images = [
        _get_page_asset('mens_jeans_detail', 'fallback_front', 'images/mens_jeans.png'),
        _get_page_asset('mens_jeans_detail', 'fallback_side', 'images/mens_jeans.png'),
        _get_page_asset('mens_jeans_detail', 'fallback_back', 'images/mens_jeans.png'),
        _get_page_asset('mens_jeans_detail', 'fallback_close', 'images/mens_jeans.png'),
    ]

    for product in products:
        variant = ProductVariant.objects.filter(product=product).first()
        image_names = [variant.image1, variant.image2, variant.image3, variant.image4] if variant else []

        valid_images = []
        for image_name in image_names:
            if not image_name:
                continue
            resolved = _asset_exists(f'images/{image_name}')
            if resolved:
                valid_images.append(resolved)

        if not valid_images:
            valid_images = [image_path for image_path in fallback_images if image_path]

        primary_image = valid_images[0] if valid_images else _get_product_image_path(product, variant)
        image_cards.append({
            'product_id': product.product_id,
            'product_name': product.product_name,
            'brand': product.brand,
            'offer_price': product.offer_price,
            'image_path': primary_image,
            'card_name': product.product_name,
        })

    return render(request, 'store/mens-Jeans.html', {
        'image_cards': image_cards,
        'logo_image': _get_site_asset('logo', 'images/logo1.png'),
        'page_background_image': _get_page_asset('mens_jeans', 'background', 'images/jeansbg.jpg'),
    })


def mens_jeans_detail(request, product_id):
    product = get_object_or_404(
        Product.objects.select_related('category', 'subcategory'),
        product_id=product_id,
        category__category_name__iexact='mens',
        subcategory__subcategory_name__iexact='jeans',
        is_active=True,
    )
    return redirect('catalog_product_detail', product_id=product.product_id)


def accessories_men(request):
    products = Product.objects.filter(
        category__category_name__iexact='mens',
        subcategory__subcategory_name__icontains='accessor',
        is_active=True,
    ).select_related('category', 'subcategory')

    return render(request, 'store/accessories-men.html', {
        'logo_image': _get_site_asset('logo', 'images/logo1.png'),
        'product_count': products.count(),
        'page_title': "Men's Accessories",
        'status_message': 'Our accessories section is currently under maintenance.',
    })


def accessories_women(request):
    products = Product.objects.filter(
        category__category_name__iexact='womens',
        is_active=True,
    ).filter(
        Q(subcategory__subcategory_name__icontains='accessor') |
        Q(subcategory__subcategory_name__icontains='bag')
    ).select_related('category', 'subcategory')

    return render(request, 'store/accessories-women.html', {
        'logo_image': _get_site_asset('logo', 'images/logo1.png'),
        'product_count': products.count(),
        'page_title': "Women's Accessories",
        'status_message': 'Our accessories section is currently under maintenance.',
    })


def womens_ethnicware(request):
    products = Product.objects.filter(
        category__category_name__iexact='womens',
        subcategory__subcategory_name__iexact='ethnic wear',
        is_active=True,
    ).select_related('category', 'subcategory')
    return render(request, 'store/product-listing-generic.html', {
        'page_title': 'Stylish Ethnic Wear for Women',
        'search_placeholder_text': 'Search ethnic wear...',
        'image_cards': _build_product_cards(products),
        'logo_image': _get_site_asset('logo', 'images/logo1.png'),
        'page_background_image': _get_page_asset('womens_ethnicware', 'background', 'images/ethicwearebg.jpeg'),
        'detail_url_name': 'catalog_product_detail',
    })


def womens_westernware(request):
    products = Product.objects.filter(
        category__category_name__iexact='womens',
        subcategory__subcategory_name__iexact='western wear',
        is_active=True,
    ).select_related('category', 'subcategory')
    return render(request, 'store/product-listing-generic.html', {
        'page_title': 'Stylish Western Wear for Women',
        'search_placeholder_text': 'Search western wear...',
        'image_cards': _build_product_cards(products),
        'logo_image': _get_site_asset('logo', 'images/logo1.png'),
        'page_background_image': _get_page_asset('womens_westernware', 'background', 'images/westernware.jpg'),
        'detail_url_name': 'catalog_product_detail',
    })


def womens_footwear(request):
    products = Product.objects.filter(
        category__category_name__iexact='womens',
        subcategory__subcategory_name__iexact='footwear',
        is_active=True,
    ).select_related('category', 'subcategory')
    return render(request, 'store/product-listing-generic.html', {
        'page_title': "Women's Footwear",
        'search_placeholder_text': 'Search footwear...',
        'image_cards': _build_product_cards(products),
        'logo_image': _get_site_asset('logo', 'images/logo1.png'),
        'page_background_image': _get_page_asset('womens_footwear', 'background', 'images/women-footwear1.png'),
        'detail_url_name': 'catalog_product_detail',
    })


def kids_tshirts(request):
    products = Product.objects.filter(
        category__category_name__iexact='kids',
        is_active=True,
    ).filter(
        Q(subcategory__subcategory_name__icontains='kids t-shirts') |
        Q(subcategory__subcategory_name__icontains='t-shirts') |
        Q(subcategory__subcategory_name__icontains='t shirts')
    ).select_related('category', 'subcategory')
    return render(request, 'store/product-listing-generic.html', {
        'page_title': 'T-Shirts for Kids',
        'search_placeholder_text': 'Search kids t-shirts...',
        'image_cards': _build_product_cards(products),
        'logo_image': _get_site_asset('logo', 'images/logo1.png'),
        'page_background_image': _get_page_asset('kids_tshirts', 'background', 'images/kidstshirtsbg.jpeg'),
        'detail_url_name': 'catalog_product_detail',
    })


def kids_dresses(request):
    products = Product.objects.filter(
        category__category_name__iexact='kids',
        is_active=True,
    ).filter(
        Q(subcategory__subcategory_name__icontains='kids dresses') |
        Q(subcategory__subcategory_name__icontains='dresses')
    ).select_related('category', 'subcategory')
    return render(request, 'store/product-listing-generic.html', {
        'page_title': 'Kids Dresses',
        'search_placeholder_text': 'Search kids dresses...',
        'image_cards': _build_product_cards(products),
        'logo_image': _get_site_asset('logo', 'images/logo1.png'),
        'page_background_image': _get_page_asset('kids_dresses', 'background', 'images/kids-dresses.png'),
        'detail_url_name': 'catalog_product_detail',
    })


def kids_toys(request):
    products = Product.objects.filter(
        category__category_name__iexact='kids',
        subcategory__subcategory_name__iexact='toys',
        is_active=True,
    ).select_related('category', 'subcategory')
    return render(request, 'store/product-listing-generic.html', {
        'page_title': 'Kids Toys',
        'search_placeholder_text': 'Search kids toys...',
        'image_cards': _build_product_cards(products),
        'logo_image': _get_site_asset('logo', 'images/logo1.png'),
        'page_background_image': _get_page_asset('kids_toys', 'background', 'images/kids-toys.png'),
        'detail_url_name': 'catalog_product_detail',
    })


def kids_footwear(request):
    products = Product.objects.filter(
        category__category_name__iexact='kids',
        subcategory__subcategory_name__iexact='footwear',
        is_active=True,
    ).select_related('category', 'subcategory')
    return render(request, 'store/product-listing-generic.html', {
        'page_title': 'Kids Footwear',
        'search_placeholder_text': 'Search kids footwear...',
        'image_cards': _build_product_cards(products),
        'logo_image': _get_site_asset('logo', 'images/logo1.png'),
        'page_background_image': _get_page_asset('kids_footwear', 'background', 'images/kids-footwear.png'),
        'detail_url_name': 'catalog_product_detail',
    })


def catalog_product_detail(request, product_id):
    product = get_object_or_404(Product.objects.select_related('category', 'subcategory'), product_id=product_id, is_active=True)
    variant = ProductVariant.objects.filter(product=product).first()
    fallback_image = _get_product_image_path(product, variant)
    size_variants = list(ProductVariant.objects.filter(product=product).exclude(size__isnull=True).exclude(size__exact='').order_by('variant_id'))
    return render(request, 'store/product-detail-generic.html', {
        'product': product,
        'variant': variant,
        'size_variants': size_variants,
        'total_stock': _get_total_stock(product),
        'logo_image': _get_site_asset('logo', 'images/logo1.png'),
        'detail_fallback_front': fallback_image,
        'detail_fallback_side': fallback_image,
        'detail_fallback_back': fallback_image,
        'detail_fallback_close': fallback_image,
    })



# Login page
def login_view(request):
    next_url = request.GET.get('next') or request.POST.get('next') or 'home'

    if request.method == 'POST':
        email = (request.POST.get('email') or '').strip()
        password = request.POST.get('password') or ''

        user = User.objects.filter(email__iexact=email).first()
        if user is None:
            messages.error(request, 'This email is not registered. Please register first.')
        else:
            authenticated_user = authenticate(request, username=user.username, password=password)

            if authenticated_user is not None:
                login(request, authenticated_user)
                _merge_session_cart_into_db(request, authenticated_user)
                _set_session_cart(request, {})
                return redirect(next_url)

            messages.error(request, 'Invalid password.')

    return render(request, 'store/login.html', {'next_url': next_url})


def logout_view(request):
    logout(request)
    return redirect('home')


def register_view(request):
    next_url = request.GET.get('next') or request.POST.get('next') or 'home'

    if request.method == 'POST':
        email = (request.POST.get('email') or '').strip().lower()
        password = request.POST.get('password') or ''
        confirm_password = request.POST.get('confirm_password') or ''

        if not email or not password:
            messages.error(request, 'Email and password are required.')
        elif password != confirm_password:
            messages.error(request, 'Passwords do not match.')
        elif User.objects.filter(email__iexact=email).exists():
            messages.error(request, 'An account with this email already exists.')
        elif User.objects.filter(username__iexact=email).exists():
            messages.error(request, 'An account with this email already exists.')
        else:
            user = User.objects.create_user(username=email, email=email, password=password)
            login(request, user)
            _merge_session_cart_into_db(request, user)
            _set_session_cart(request, {})
            return redirect(next_url)

    return render(request, 'store/register.html', {'next_url': next_url})

# Cart page
def cart(request):
    if not request.user.is_authenticated:
        return redirect(f"{reverse('login')}?next=/cart/")

    cart_data = _get_effective_cart_data(request)
    cart_items, subtotal, total_items = _build_cart_summary(cart_data)

    return render(request, 'store/cart.html', {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'total_items': total_items,
        'logo_image': _get_site_asset('logo', 'images/logo1.png'),
    })


def payment_gateway(request):
    if not request.user.is_authenticated:
        return redirect(f"{reverse('login')}?next=/payment/")

    cart_data = _get_effective_cart_data(request)
    cart_items, subtotal, total_items = _build_cart_summary(cart_data)
    razorpay_error = ''

    if not _is_razorpay_configured():
        razorpay_error = 'Razorpay keys are not configured yet. Add your key ID and secret to enable checkout.'

    return render(request, 'store/payment.html', {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'total_items': total_items,
        'logo_image': _get_site_asset('logo', 'images/logo1.png'),
        'default_email': request.user.email,
        'default_full_name': request.user.get_full_name() or request.user.username,
        'default_phone_number': '8247624897',
        'payment_provider_name': 'Razorpay',
        'manual_payment_link': 'https://razorpay.me/@varshakshopeasy',
        'upi_payment_link': 'upi://pay?pa=8247624897-3@ybl&pn=VarshakShopeasy&cu=INR',
        'upi_id': '8247624897-3@ybl',
        'manual_payment_provider_name': 'Razorpay Payment Link',
        'payment_qr_image': _get_page_asset('payment_gateway', 'scanner_qr', 'images/QrCode.jpeg'),
        'razorpay_enabled': _is_razorpay_configured(),
        'razorpay_key_id': getattr(settings, 'RAZORPAY_KEY_ID', ''),
        'razorpay_order_id': '',
        'razorpay_amount_paise': int((subtotal * Decimal('100')).quantize(Decimal('1'))) if subtotal else 0,
        'razorpay_currency': 'INR',
        'razorpay_error': razorpay_error,
    })


def add_to_cart(request, product_id):
    if not request.user.is_authenticated:
        return redirect(f"{reverse('login')}?next=/product/{product_id}/")

    if request.method != 'POST':
        return redirect('product_detail', product_id=product_id)

    product = get_object_or_404(Product, product_id=product_id, is_active=True)
    quantity = max(1, int(request.POST.get('quantity', 1)))
    selected_size = (request.POST.get('selected_size') or '').strip() or None
    added, available_stock = _set_user_cart_item(request.user, product, quantity, selected_size=selected_size)
    if not added:
        messages.error(request, 'This product is out of stock.')
        return redirect('product_detail', product_id=product_id)

    if quantity > available_stock:
        messages.warning(request, f'Only {available_stock} item(s) are available, so the quantity was limited.')
    _set_session_cart(request, {})

    return redirect('cart')


def remove_from_cart(request, cart_item_id):
    if not request.user.is_authenticated:
        return redirect(f"{reverse('login')}?next=/cart/")

    if request.method != 'POST':
        return redirect('cart')

    CartItem.objects.filter(user=request.user, cart_item_id=cart_item_id).delete()
    _set_session_cart(request, {})

    return redirect('cart')


def buy_now(request, product_id):
    if not request.user.is_authenticated:
        return redirect(f"{reverse('login')}?next=/product/{product_id}/")

    if request.method != 'POST':
        return redirect('product_detail', product_id=product_id)

    product = get_object_or_404(Product, product_id=product_id, is_active=True)
    quantity = max(1, int(request.POST.get('quantity', 1)))
    selected_size = (request.POST.get('selected_size') or '').strip() or None
    variant = ProductVariant.objects.filter(product=product, size__iexact=selected_size).first() if selected_size else ProductVariant.objects.filter(product=product).first()
    available_stock = max(0, getattr(variant, 'quantity', 0) or 0) if selected_size else sum(ProductVariant.objects.filter(product=product).values_list('quantity', flat=True))
    if available_stock == 0:
        messages.error(request, 'This product is out of stock.')
        return redirect('product_detail', product_id=product_id)

    CartItem.objects.filter(user=request.user).exclude(product=product).delete()
    if quantity > available_stock:
        messages.warning(request, f'Only {available_stock} item(s) are available, so the quantity was limited.')
    _set_user_cart_item(request.user, product, quantity, selected_size=selected_size, replace=True)
    _set_session_cart(request, {})

    return redirect('payment_gateway')


@transaction.atomic
def place_order(request):
    if not request.user.is_authenticated:
        return redirect(f"{reverse('login')}?next=/payment/")

    if request.method != 'POST':
        return redirect('payment_gateway')

    cart_data = _get_effective_cart_data(request)
    cart_items, subtotal, total_items = _build_cart_summary(cart_data)

    if not cart_items:
        messages.error(request, 'Your cart is empty.')
        return redirect('cart')

    full_name = (request.POST.get('full_name') or '').strip()
    phone_number = (request.POST.get('phone_number') or '').strip()
    email = (request.POST.get('email') or '').strip()
    address = (request.POST.get('address') or '').strip()
    city = (request.POST.get('city') or '').strip()
    state = (request.POST.get('state') or '').strip()
    pincode = (request.POST.get('pincode') or '').strip()
    country = (request.POST.get('country') or 'India').strip() or 'India'
    payment_method = (request.POST.get('payment_method') or 'Card').strip() or 'Card'

    required_values = [full_name, phone_number, email, address, city, state, pincode]
    if any(not value for value in required_values):
        messages.error(request, 'Please fill in all billing details before placing the order.')
        return redirect('payment_gateway')

    order = Order.objects.create(
        user=request.user,
        full_name=full_name,
        phone_number=phone_number,
        email=email,
        address=address,
        city=city,
        state=state,
        pincode=pincode,
        country=country,
        payment_method=payment_method,
        subtotal=subtotal,
        total_items=total_items,
        status='Placed',
    )

    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item['product'],
            selected_size=item.get('selected_size'),
            quantity=item['quantity'],
            unit_price=item['product'].offer_price,
            line_total=item['line_total'],
        )

    CartItem.objects.filter(user=request.user).delete()
    _set_session_cart(request, {})
    messages.success(request, f'Order #{order.order_id} placed successfully.')
    return redirect('order_success', order_id=order.order_id)


@transaction.atomic
def verify_razorpay_payment(request):
    if not request.user.is_authenticated:
        return redirect(f"{reverse('login')}?next=/payment/")

    if request.method != 'POST':
        return redirect('payment_gateway')

    cart_data = _get_effective_cart_data(request)
    cart_items, subtotal, total_items = _build_cart_summary(cart_data)

    if not cart_items:
        messages.error(request, 'Your cart is empty.')
        return redirect('cart')

    full_name = (request.POST.get('full_name') or '').strip()
    phone_number = (request.POST.get('phone_number') or '').strip()
    email = (request.POST.get('email') or '').strip()
    address = (request.POST.get('address') or '').strip()
    city = (request.POST.get('city') or '').strip()
    state = (request.POST.get('state') or '').strip()
    pincode = (request.POST.get('pincode') or '').strip()
    country = (request.POST.get('country') or 'India').strip() or 'India'
    local_order_id = (request.POST.get('local_order_id') or '').strip()
    razorpay_order_id = (request.POST.get('razorpay_order_id') or '').strip()
    razorpay_payment_id = (request.POST.get('razorpay_payment_id') or '').strip()
    razorpay_signature = (request.POST.get('razorpay_signature') or '').strip()

    required_values = [
        full_name, phone_number, email, address, city, state, pincode,
        local_order_id, razorpay_order_id, razorpay_payment_id, razorpay_signature,
    ]
    if any(not value for value in required_values):
        messages.error(request, 'Payment verification details are missing. Please try again.')
        return redirect('payment_gateway')

    if not _is_razorpay_configured():
        messages.error(request, 'Razorpay is not configured on the backend yet.')
        return redirect('payment_gateway')

    if not _verify_razorpay_signature(razorpay_order_id, razorpay_payment_id, razorpay_signature):
        messages.error(request, 'Payment signature verification failed.')
        return redirect('payment_gateway')

    try:
        payment_data = _fetch_razorpay_payment(razorpay_payment_id)
    except requests.RequestException:
        messages.error(request, 'Unable to confirm the payment with Razorpay right now. Please try again.')
        return redirect('payment_gateway')

    expected_amount = int((subtotal * Decimal('100')).quantize(Decimal('1')))
    payment_status = (payment_data.get('status') or '').lower()
    payment_amount = int(payment_data.get('amount') or 0)
    payment_order_id = payment_data.get('order_id') or ''

    if payment_order_id != razorpay_order_id or payment_amount != expected_amount or payment_status not in {'authorized', 'captured'}:
        messages.error(request, 'Payment could not be validated against the order details.')
        return redirect('payment_gateway')

    order = get_object_or_404(
        Order,
        order_id=local_order_id,
        user=request.user,
        razorpay_order_id=razorpay_order_id,
    )

    order.full_name = full_name
    order.phone_number = phone_number
    order.email = email
    order.address = address
    order.city = city
    order.state = state
    order.pincode = pincode
    order.country = country
    order.payment_method = 'Razorpay'
    order.payment_status = payment_status.title()
    order.currency = payment_data.get('currency') or 'INR'
    order.razorpay_payment_id = razorpay_payment_id
    order.razorpay_signature = razorpay_signature
    order.status = 'Placed'
    order.subtotal = subtotal
    order.total_items = total_items
    order.save(update_fields=[
        'full_name', 'phone_number', 'email', 'address', 'city', 'state',
        'pincode', 'country', 'payment_method', 'payment_status', 'currency',
        'razorpay_payment_id', 'razorpay_signature', 'status', 'subtotal',
        'total_items',
    ])

    CartItem.objects.filter(user=request.user).delete()
    _set_session_cart(request, {})
    messages.success(request, f'Payment verified and order #{order.order_id} placed successfully.')
    return redirect('order_success', order_id=order.order_id)


@transaction.atomic
def create_razorpay_checkout(request):
    if not request.user.is_authenticated:
        return JsonResponse({'ok': False, 'message': 'Login required.'}, status=401)

    if request.method != 'POST':
        return JsonResponse({'ok': False, 'message': 'Invalid request method.'}, status=405)

    if not _is_razorpay_configured():
        return JsonResponse({'ok': False, 'message': 'Razorpay is not configured on the backend yet.'}, status=400)

    cart_data = _get_effective_cart_data(request)
    cart_items, subtotal, total_items = _build_cart_summary(cart_data)

    if not cart_items:
        return JsonResponse({'ok': False, 'message': 'Your cart is empty.'}, status=400)

    full_name = (request.POST.get('full_name') or '').strip()
    phone_number = (request.POST.get('phone_number') or '').strip()
    email = (request.POST.get('email') or '').strip()
    address = (request.POST.get('address') or '').strip()
    city = (request.POST.get('city') or '').strip()
    state = (request.POST.get('state') or '').strip()
    pincode = (request.POST.get('pincode') or '').strip()
    country = (request.POST.get('country') or 'India').strip() or 'India'

    required_values = [full_name, phone_number, email, address, city, state, pincode]
    if any(not value for value in required_values):
        return JsonResponse({'ok': False, 'message': 'Please fill in all billing details.'}, status=400)

    amount_paise = int((subtotal * Decimal('100')).quantize(Decimal('1')))

    order = Order.objects.create(
        user=request.user,
        full_name=full_name,
        phone_number=phone_number,
        email=email,
        address=address,
        city=city,
        state=state,
        pincode=pincode,
        country=country,
        payment_method='Razorpay',
        payment_status='Created',
        currency='INR',
        subtotal=subtotal,
        total_items=total_items,
        status='Pending Payment',
    )

    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item['product'],
            selected_size=item.get('selected_size'),
            quantity=item['quantity'],
            unit_price=item['product'].offer_price,
            line_total=item['line_total'],
        )

    try:
        razorpay_order = _create_razorpay_order(
            amount_paise=amount_paise,
            receipt=_build_razorpay_receipt(request.user.id),
            notes={
                'user_id': str(request.user.id),
                'local_order_id': str(order.order_id),
                'email': email,
            },
        )
    except (requests.RequestException, ValueError) as exc:
        order.payment_status = 'Failed'
        order.status = 'Payment Failed'
        order.save(update_fields=['payment_status', 'status'])
        return JsonResponse({'ok': False, 'message': _friendly_razorpay_error(exc)}, status=400)

    order.razorpay_order_id = razorpay_order.get('id')
    order.save(update_fields=['razorpay_order_id'])

    return JsonResponse({
        'ok': True,
        'local_order_id': order.order_id,
        'razorpay_order_id': razorpay_order.get('id', ''),
        'amount': amount_paise,
        'currency': razorpay_order.get('currency', 'INR'),
        'key_id': getattr(settings, 'RAZORPAY_KEY_ID', ''),
        'customer': {
            'name': full_name,
            'email': email,
            'contact': phone_number,
        },
    })


def order_success(request, order_id):
    if not request.user.is_authenticated:
        return redirect(f"{reverse('login')}?next=/orders/{order_id}/success/")

    order = get_object_or_404(Order.objects.prefetch_related('items__product'), order_id=order_id, user=request.user)
    order_items = []
    for item in order.items.all():
        variant = ProductVariant.objects.filter(
            product=item.product,
            size__iexact=item.selected_size,
        ).first() if item.selected_size else ProductVariant.objects.filter(product=item.product).first()
        order_items.append({
            'product': item.product,
            'selected_size': item.selected_size,
            'quantity': item.quantity,
            'unit_price': item.unit_price,
            'line_total': item.line_total,
            'image_path': _get_product_image_path(item.product, variant),
        })

    return render(request, 'store/order-success.html', {
        'order': order,
        'order_items': order_items,
        'logo_image': _get_site_asset('logo', 'images/logo1.png'),
    })


def orders(request):
    if not request.user.is_authenticated:
        return redirect(f"{reverse('login')}?next=/orders/")

    user_orders = Order.objects.filter(user=request.user).prefetch_related('items__product')
    return render(request, 'store/orders.html', {
        'orders': user_orders,
        'logo_image': _get_site_asset('logo', 'images/logo1.png'),
    })


SHOP_ADMIN_EMAIL = 'saivarshak14@gmail.com'


def _is_shop_admin(user):
    return user.is_authenticated and user.email.lower() == SHOP_ADMIN_EMAIL.lower()


def _require_shop_admin(request):
    if _is_shop_admin(request.user):
        return None
    return redirect(f"{reverse('admin_access')}?next={request.path}")


def admin_access(request):
    next_url = request.GET.get('next') or request.POST.get('next') or reverse('admin_dashboard')

    if _is_shop_admin(request.user):
        return redirect(next_url)

    if request.method == 'POST':
        email = (request.POST.get('email') or '').strip().lower()
        password = request.POST.get('password') or ''
        user = User.objects.filter(email__iexact=email).first()

        if email != SHOP_ADMIN_EMAIL.lower():
            messages.error(request, 'Only the configured admin email can access this panel.')
        elif user is None:
            messages.error(request, 'Admin user not found in backend.')
        else:
            authenticated_user = authenticate(request, username=user.username, password=password)
            if authenticated_user is None:
                messages.error(request, 'Invalid admin password.')
            else:
                login(request, authenticated_user)
                return redirect(next_url)

    return render(request, 'store/admin-login.html', {
        'next_url': next_url,
        'admin_email': SHOP_ADMIN_EMAIL,
        'logo_image': _get_site_asset('logo', 'images/logo1.png'),
    })


def admin_dashboard(request):
    access_redirect = _require_shop_admin(request)
    if access_redirect:
        return access_redirect

    products = Product.objects.select_related('category', 'subcategory').order_by('-product_id')
    product_rows = []
    for product in products:
        variant = ProductVariant.objects.filter(product=product).first()
        product_rows.append({
            'product': product,
            'variant': variant,
            'total_stock': _get_total_stock(product),
            'image_path': _get_product_image_path(product, variant),
        })

    return render(request, 'store/dashboard.html', {
        'products': product_rows,
        'logo_image': _get_site_asset('logo', 'images/logo1.png'),
    })


def _parse_decimal(raw_value, default='0'):
    try:
        return Decimal((raw_value or default).strip())
    except (InvalidOperation, AttributeError):
        return Decimal(default)


def _parse_size_quantities(raw_value):
    variants = []
    if not raw_value:
        return variants

    lines = [line.strip() for line in raw_value.replace(',', '\n').splitlines() if line.strip()]
    for line in lines:
        if ':' not in line:
            continue
        size, quantity = line.split(':', 1)
        size = size.strip()
        quantity = quantity.strip()
        if not size:
            continue
        try:
            parsed_quantity = max(0, int(quantity))
        except ValueError:
            continue
        variants.append((size, parsed_quantity))
    return variants


def _get_total_stock(product):
    return sum(ProductVariant.objects.filter(product=product).values_list('quantity', flat=True))


def _save_uploaded_product_image(uploaded_file, product_name, slot_name):
    if not uploaded_file:
        return None

    extension = Path(uploaded_file.name).suffix or '.jpg'
    safe_name = slugify(product_name) or 'product'
    filename = f"{safe_name}_{slot_name}{extension.lower()}"
    target_dir = Path(settings.BASE_DIR) / 'static' / 'images'
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / filename

    counter = 1
    while target_path.exists():
        filename = f"{safe_name}_{slot_name}_{counter}{extension.lower()}"
        target_path = target_dir / filename
        counter += 1

    with target_path.open('wb+') as destination:
        for chunk in uploaded_file.chunks():
            destination.write(chunk)

    return filename


def admin_product_form(request, product_id=None):
    access_redirect = _require_shop_admin(request)
    if access_redirect:
        return access_redirect

    product = Product.objects.filter(product_id=product_id).first() if product_id else None
    variant = ProductVariant.objects.filter(product=product).first() if product else None
    existing_variants = list(ProductVariant.objects.filter(product=product).order_by('variant_id')) if product else []
    categories = Category.objects.order_by('category_name')
    subcategories = SubCategory.objects.select_related('category').order_by('subcategory_name')

    if request.method == 'POST':
        product_name = (request.POST.get('product_name') or '').strip()
        brand = (request.POST.get('brand') or '').strip()
        category_id = request.POST.get('category_id')
        subcategory_id = request.POST.get('subcategory_id')
        sku = (request.POST.get('sku') or '').strip()
        price = _parse_decimal(request.POST.get('price'))
        discount_percent = _parse_decimal(request.POST.get('discount_percent'))
        description = (request.POST.get('description') or '').strip()
        size = (request.POST.get('size') or '').strip()
        size_quantities_raw = (request.POST.get('size_quantities') or '').strip()
        color = (request.POST.get('color') or '').strip()
        quantity = max(0, int(request.POST.get('quantity') or 0))
        image1 = (request.POST.get('image1') or '').strip() or None
        image2 = (request.POST.get('image2') or '').strip() or None
        image3 = (request.POST.get('image3') or '').strip() or None
        image4 = (request.POST.get('image4') or '').strip() or None
        image1_upload = request.FILES.get('image1_upload')
        image2_upload = request.FILES.get('image2_upload')
        image3_upload = request.FILES.get('image3_upload')
        image4_upload = request.FILES.get('image4_upload')
        is_active = request.POST.get('is_active') == 'on'

        category = Category.objects.filter(category_id=category_id).first()
        subcategory = SubCategory.objects.filter(subcategory_id=subcategory_id).first()

        if not all([product_name, category, subcategory, sku]):
            messages.error(request, 'Product name, category, subcategory, and SKU are required.')
        else:
            product_values = {
                'product_name': product_name,
                'brand': brand or None,
                'category_id': category.category_id,
                'subcategory_id': subcategory.subcategory_id,
                'sku': sku,
                'price': price,
                'discount_percent': discount_percent,
                'description': description or None,
                'is_active': is_active,
            }

            if product is None:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO products
                        (product_name, brand, category_id, subcategory_id, sku, price, discount_percent, description, is_active)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        [
                            product_values['product_name'],
                            product_values['brand'],
                            product_values['category_id'],
                            product_values['subcategory_id'],
                            product_values['sku'],
                            product_values['price'],
                            product_values['discount_percent'],
                            product_values['description'],
                            product_values['is_active'],
                        ],
                    )
                    product = Product.objects.get(product_id=cursor.lastrowid)
            else:
                Product.objects.filter(product_id=product.product_id).update(**product_values)
                product.refresh_from_db()

            if variant is None:
                variant = ProductVariant(product=product)

            uploaded_image1_name = _save_uploaded_product_image(image1_upload, product.product_name, 'image1')
            uploaded_image2_name = _save_uploaded_product_image(image2_upload, product.product_name, 'image2')
            uploaded_image3_name = _save_uploaded_product_image(image3_upload, product.product_name, 'image3')
            uploaded_image4_name = _save_uploaded_product_image(image4_upload, product.product_name, 'image4')

            final_image1 = uploaded_image1_name or image1
            final_image2 = uploaded_image2_name or image2
            final_image3 = uploaded_image3_name or image3
            final_image4 = uploaded_image4_name or image4
            size_variants = _parse_size_quantities(size_quantities_raw)

            if size_variants:
                ProductVariant.objects.filter(product=product).delete()
                for variant_size, variant_quantity in size_variants:
                    ProductVariant.objects.create(
                        product=product,
                        size=variant_size,
                        color=color or None,
                        quantity=variant_quantity,
                        image1=final_image1,
                        image2=final_image2,
                        image3=final_image3,
                        image4=final_image4,
                    )
            else:
                variant.size = size or None
                variant.color = color or None
                variant.quantity = quantity
                variant.image1 = final_image1
                variant.image2 = final_image2
                variant.image3 = final_image3
                variant.image4 = final_image4
                variant.save()

            messages.success(request, 'Product saved successfully.')
            return redirect('admin_dashboard')

    return render(request, 'store/upload.html', {
        'product': product,
        'variant': variant,
        'size_quantities_value': '\n'.join(
            f"{item.size}: {item.quantity}" for item in existing_variants if item.size
        ),
        'categories': categories,
        'subcategories': subcategories,
        'logo_image': _get_site_asset('logo', 'images/logo1.png'),
        'page_title': 'Edit Product' if product else 'Add Product',
        'form_action_label': 'Update Product' if product else 'Add Product',
    })


def admin_product_delete(request, product_id):
    access_redirect = _require_shop_admin(request)
    if access_redirect:
        return access_redirect

    product = get_object_or_404(Product, product_id=product_id)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully.')
    return redirect('admin_dashboard')


def mens_shirts(request):
    products = Product.objects.filter(
        category__category_name__iexact='mens',
        subcategory__subcategory_name__iexact='shirts',
        is_active=True,
    ).select_related('category', 'subcategory')

    image_cards = []

    for product in products:
        variant = ProductVariant.objects.filter(product=product).first()
        image_names = [variant.image1, variant.image2, variant.image3, variant.image4] if variant else []

        valid_images = []
        for image_name in image_names:
            if not image_name:
                continue
            image_path = Path(settings.BASE_DIR) / 'static' / 'images' / image_name
            if image_path.exists():
                valid_images.append(f'images/{image_name}')

        if not valid_images:
            valid_images = [_get_product_image_path(product, variant)]

        primary_image = valid_images[0] if valid_images else _get_product_image_path(product, variant)
        image_cards.append({
            'product_id': product.product_id,
            'product_name': product.product_name,
            'brand': product.brand,
            'offer_price': product.offer_price,
            'image_path': primary_image,
            'card_name': product.product_name,
        })

    return render(request, 'store/mens-shirts.html', {
        'image_cards': image_cards,
        'logo_image': _get_site_asset('logo', 'images/logo1.png'),
        'page_background_image': _get_page_asset('mens_shirts', 'background', 'images/shirt.jpg'),
    })

# Optional: Django REST Framework API
# Only add this if you installed DRF
from rest_framework import viewsets
from .serializers import ProductSerializer  # you need this serializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer 
