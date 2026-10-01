from django.contrib import admin
from django.urls import include, path
from store import views

urlpatterns = [
    # Google OAuth / Social Auth
    path('auth/', include('social_django.urls', namespace='social')),

    # Django's built-in administration stays at the conventional URL. The
    # existing ShopEase control center remains at /admin-panel/ and /shop-admin/.
    path('admin/', admin.site.urls),
    path('shop-admin/', views.admin_dashboard, name='shop_admin_dashboard'),
    path('admin_panel/', views.admin_control_center, name='admin_control_center'),
    path('admin-access/', views.admin_access, name='admin_access'),
    
    # Store URLs
    path('', include('store.urls')),
]
