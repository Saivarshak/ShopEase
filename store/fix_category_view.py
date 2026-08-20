from pathlib import Path
import re

path = Path("store/views.py")
text = path.read_text(encoding="utf-8")

pattern = r"def category_view\(request, category_name\):.*?return render\(request, template_name, context\)\n"

replacement = r'''def category_view(request, category_name):
    category_lookup = {
        "men": "mens",
        "women": "womens",
        "kids": "kids",
    }

    canonical_root_urls = {
        "men": "/men/",
        "mens": "/men/",
        "women": "/women/",
        "womens": "/women/",
        "kids": "/kids/",
    }

    requested_key = (category_name or "").lower()

    if request.path.startswith("/category") and requested_key in canonical_root_urls:
        return redirect(canonical_root_urls[requested_key], permanent=True)

    template_lookup = {
        "mens": "store/category-men.html",
        "womens": "store/category-women.html",
        "kids": "store/category-kids.html",
    }

    normalized = category_lookup.get(requested_key, requested_key)

    category = get_object_or_404(
        Category,
        category_name__iexact=normalized,
    )

    products = (
        Product.objects.filter(category=category, is_active=True)
        .select_related("category", "subcategory")
        .prefetch_related("productvariant_set")
    )

    template_name = template_lookup.get(
        category.category_name.lower(),
        "store/category-men.html",
    )

    context = {
        "products": products,
        "category": category,
    }

    root = FashionCategory.objects.filter(
        root_category=category,
        parent__isnull=True,
    ).first()

    fashion_categories = (
        FashionCategory.objects.filter(
            parent=root,
            is_active=True,
        ).order_by("sort_order")
        if root
        else FashionCategory.objects.none()
    )

    if category.category_name.lower() == "mens":
        fallback_map = {
            "t-shirts": "images/T-shirt.jpg",
            "shirts": "images/mens_shirts.png",
            "jeans": "images/mens_jeans.png",
            "accessories": "images/mens_accessories.png",
        }

        context["men_categories"] = (
            _build_fashion_category_cards(category)
            or _load_category_cards(
                fashion_categories,
                fallback_map,
                "images/T-shirt.jpg",
            )
        )

        context["page_background_image"] = _get_page_asset(
            "category_men",
            "background",
            "images/bg.jpg",
        )

    elif category.category_name.lower() == "womens":
        fallback_map = {
            "ethnic wear": "images/women-ethnic.png",
            "western wear": "images/women-western.png",
            "footwear": "images/women-footwear1.png",
            "bags & accessories": "images/women-bags.png",
            "bags and accessories": "images/women-bags.png",
        }

        context["women_categories"] = (
            _build_fashion_category_cards(category)
            or _load_category_cards(
                fashion_categories,
                fallback_map,
                "images/women.png",
            )
        )

        context["page_background_image"] = _get_page_asset(
            "category_women",
            "background",
            "images/womenbg.jpg",
        )

    elif category.category_name.lower() == "kids":
        fallback_map = {
            "t-shirts": "images/kids-tshirts.png",
            "kids dresses": "images/kids-dresses.png",
            "dresses": "images/kids-dresses.png",
            "toys": "images/kids-toys.png",
            "footwear": "images/kids-footwear.png",
        }

        context["kids_categories"] = (
            _build_fashion_category_cards(category)
            or _load_category_cards(
                fashion_categories,
                fallback_map,
                "images/kids.png",
            )
        )

        context["page_background_image"] = _get_page_asset(
            "category_kids",
            "background",
            "images/kidsbg.jpg",
        )

    context["page_background_url"] = _asset_public_url(
        context["page_background_image"]
    )

    context["logo_image"] = _get_site_asset(
        "logo",
        "images/logo1.png",
    )

    return render(request, template_name, context)
'''

new_text, count = re.subn(pattern, replacement, text, flags=re.S)

if count != 1:
    raise SystemExit(f"Expected to replace 1 block, replaced {count}")

path.write_text(new_text, encoding="utf-8")

print("✓ category_view updated successfully")