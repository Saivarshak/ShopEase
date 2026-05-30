from django.urls import path, include
from . import views

# Optional: DRF API router
from rest_framework import routers

router = routers.DefaultRouter()
# Only enable this if ProductViewSet exists
router.register('products', views.ProductViewSet)

urlpatterns = [
    path('assets/<path:asset_path>', views.store_asset, name='store_asset'),

    # DRF API
    path('api/', include(router.urls)),     

    # Home page
    path('', views.home, name='home'),
    path('contact-us/', views.contact_us, name='contact_us'),
    path('contact.html', views.contact_us, name='contact_html'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('refund-policy/', views.refund_policy, name='refund_policy'),
    path('terms-and-conditions/', views.terms_and_conditions, name='terms_and_conditions'),
    path('search/', views.search_results, name='search_results'),
    
    path('mens_tshirts', views.mens_tshirts, name='mens_tshirts_legacy'),
    path('mens_tshirts/', views.mens_tshirts, name='mens_tshirts'),
    path('mens_tshirts/<int:product_id>/', views.mens_tshirt_detail, name='mens_tshirt_detail'),
    path('mens_shirts/', views.mens_shirts, name='mens_shirts'),
    path('mens_jeans/', views.mens_jeans, name='mens_jeans'),
    path('mens_jeans/<int:product_id>/', views.mens_jeans_detail, name='mens_jeans_detail'),
    path('accessories_men/', views.accessories_men, name='accessories_men'),
    path('accessories_women/', views.accessories_women, name='accessories_women'),
    path('womens_ethnicware/', views.womens_ethnicware, name='womens_ethnicware'),
    path('womens_westernware/', views.womens_westernware, name='womens_westernware'),
    path('womens_footwear/', views.womens_footwear, name='womens_footwear'),
    path('kids_tshirts/', views.kids_tshirts, name='kids_tshirts'),
    path('kids_dresses/', views.kids_dresses, name='kids_dresses'),
    path('kids_toys/', views.kids_toys, name='kids_toys'),
    path('kids_footwear/', views.kids_footwear, name='kids_footwear'),
    path('catalog/product/<int:product_id>/', views.catalog_product_detail, name='catalog_product_detail'),
    path('mens_shirt1_detailed/', views.product_detail, {'product_id': 27}, name='mens_shirt1_detailed'),
    
    # Login and Cart
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('admin-access/', views.admin_access, name='admin_access'),
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/fashion-structure/', views.admin_fashion_structure, name='admin_fashion_structure'),
    path('admin-panel/backgrounds/', views.admin_backgrounds, name='admin_backgrounds'),
    path('admin-panel/products/add/', views.admin_product_form, name='admin_product_add'),
    path('admin-panel/products/<int:product_id>/edit/', views.admin_product_form, name='admin_product_edit'),
    path('admin-panel/products/<int:product_id>/delete/', views.admin_product_delete, name='admin_product_delete'),
    path('cart/', views.cart, name='cart'),
    path('payment/', views.payment_gateway, name='payment_gateway'),
    path('payment/start/', views.start_payment_gateway, name='start_payment_gateway'),
    path('payment/create/', views.create_razorpay_checkout, name='create_razorpay_checkout'),
    path('payment/verify/', views.verify_razorpay_payment, name='verify_razorpay_payment'),
    path('payment/webhook/', views.razorpay_webhook, name='razorpay_webhook'),
    path('payment/callback/', views.razorpay_payment_link_callback, name='razorpay_payment_link_callback'),
    path('place-order/', views.place_order, name='place_order'),
    path('orders/', views.orders, name='orders'),
    path('orders/<int:order_id>/success/', views.order_success, name='order_success'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/remove/session/<path:item_key>/', views.remove_session_cart_item, name='remove_session_cart_item'),
    path('buy-now/<int:product_id>/', views.buy_now, name='buy_now'),

    # Dynamic category pages
    path('category/<str:category_name>/', views.category_view, name='category'),
    

    # Shortcut URLs for Men/Women/Kids
    path('category_men/', views.category_view, {'category_name': 'men'}, name='category_men'),
    path('category_women/', views.category_view, {'category_name': 'women'}, name='category_women'),
    path('category_kids/', views.category_view, {'category_name': 'kids'}, name='category_kids'),

    # Dynamic product detail
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
]

