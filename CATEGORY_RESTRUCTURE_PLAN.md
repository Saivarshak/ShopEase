# Category Rooting Implementation Plan

## Updated Database Schema

- `store.Product.slug` stores canonical product slugs for `/men/.../<productSlug>/` style URLs.
- `store.FashionCategory.banner_image` stores optional category banner images uploaded from admin.
- Existing `Category`, `SubCategory`, `Product`, `ProductVariant`, `Order`, `OrderItem`, `CartItem`, `WishlistItem`, and user tables remain intact.
- `FashionCategory.is_active` represents Active vs Hidden.
- `FashionCategory.is_under_maintenance` represents Under Maintenance.

## Migration Strategy

- Migration `store.0014_root_fashion_hierarchy` seeds the new root hierarchy:
  - Men
  - Women
  - Kids
  - Accessories > Common For All Genders
- Existing products keep their primary keys, SKUs, prices, variants, inventory, order history, carts, accounts, and payments.
- Product slugs are generated only when missing.
- Existing product category/subcategory combinations are mapped to the nearest new `FashionCategory`.
- Legacy `Category` and `SubCategory` records are retained as compatibility anchors for old reports and admin screens.

## Frontend Routes

- Root pages:
  - `/men/`
  - `/women/`
  - `/kids/`
  - `/accessories/common/`
- Category listing examples:
  - `/men/casual-wear/t-shirts/`
  - `/women/casual-wear/t-shirts/`
  - `/kids/casual-wear/t-shirts/`
- Product detail examples:
  - `/men/casual-wear/t-shirts/<productSlug>/`
  - `/women/casual-wear/<productSlug>/`

## Backend/API Changes

- Existing product API remains read-only and continues to serialize all product fields, including the new `slug`.
- Slug routes render through the existing generic product listing/detail views.
- Product movement in admin updates both `Product.fashion_category` and legacy `Product.category`/`Product.subcategory`.

## Admin Dashboard Changes

- Admins can create, edit, hide, delete, and move nested `FashionCategory` records.
- Admins can assign products to gender-specific categories.
- Category image and banner uploads are supported.
- Category status controls:
  - Active: `is_active=True`
  - Hidden: `is_active=False`
  - Under Maintenance: `is_under_maintenance=True`
- Dragging category cards in `admin-panel/categories/` renumbers sort order fields before saving.

## SEO Redirect Rules

- Old numeric category routes redirect permanently to canonical slug routes.
- Old product ID routes redirect permanently to canonical product slug routes when a fashion category is available.
- Legacy storefront URLs redirect permanently:
  - `/mens_tshirts/` -> `/men/casual-wear/t-shirts/`
  - `/mens_jeans/` -> `/men/casual-wear/jeans/`
  - `/mens_shirts/` -> `/men/formal-wear/formal-shirts/`
  - `/womens_ethnicware/` -> `/women/casual-wear/`
  - `/womens_westernware/` -> `/women/casual-wear/`
  - `/womens_footwear/` -> `/women/footwear/`
  - `/kids_tshirts/` -> `/kids/casual-wear/t-shirts/`
  - `/kids_dresses/` -> `/kids/formal-wear/`
  - `/kids_toys/` -> `/kids/accessories/`
  - `/kids_footwear/` -> `/kids/footwear/`
  - `/category_men/` -> `/men/`
  - `/category_women/` -> `/women/`
  - `/category_kids/` -> `/kids/`

## Folder Structure Updates

- No app rebuild or folder reorganization was required.
- New migration added under `store/migrations/`.
- Category behavior remains in `store/models.py`, `store/views.py`, `store/urls.py`, and existing templates.

## Sample Seed Data

- Men, Women, and Kids each receive:
  - Casual Wear: T-Shirts, Polo Shirts, Jeans, Hoodies & Sweatshirts, Shorts, Dresses
  - Formal Wear: Formal Shirts, Suits, Blazers, Dress Trousers, Tuxedos
  - Ethnic Wear: Kurtas, Sarees, Lehengas, Sherwanis, Ethnic Dresses
  - Footwear: Sneakers, Sandals, Boots, Dress Shoes, Loafers
  - Accessories: Bags, Belts, Watches, Sunglasses, Wallets, Toys
- Top-level Accessories receives:
  - Common For All Genders
  - Bags, Watches, Sunglasses, Wallets, Other Future Accessories
  - Default status: Under Maintenance

## Rollout Plan

1. Back up production database.
2. Deploy code and run `python manage.py migrate`.
3. Review admin category tree and adjust product mappings where needed.
4. Confirm old URLs return 301 redirects.
5. Activate shared Accessories from admin when ready.
