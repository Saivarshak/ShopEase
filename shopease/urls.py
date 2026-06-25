"""
URL configuration for shopease project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.db import connection
from django.db.utils import OperationalError, ProgrammingError
from django.http import JsonResponse
from django.urls import path, include
from django.shortcuts import redirect

REQUIRED_STORE_TABLES = {
    'categories',
    'subcategories',
    'fashion_categories',
    'products',
    'product_variants',
    'cart_items',
    'orders',
    'order_items',
    'wishlist_items',
    'user_addresses',
    'men_categories',
    'women_categories',
    'kids_categories',
    'site_assets',
    'page_assets',
    'home_content',
}


def redirect_admin(request):
    return redirect('admin_access')


def healthcheck(request):
    try:
        connection.ensure_connection()
        existing_tables = set(connection.introspection.table_names())
    except (OperationalError, ProgrammingError) as exc:
        return JsonResponse({
            'ok': False,
            'database': connection.vendor,
            'error': str(exc),
        }, status=503)

    missing_tables = sorted(REQUIRED_STORE_TABLES - existing_tables)
    if missing_tables:
        return JsonResponse({
            'ok': False,
            'database': connection.vendor,
            'missing_tables': missing_tables,
        }, status=503)

    return JsonResponse({
        'ok': True,
        'database': connection.vendor,
        'tables_checked': sorted(REQUIRED_STORE_TABLES),
    })

urlpatterns = [
    path('admin/', redirect_admin),
    path('health/', healthcheck, name='healthcheck'),
    path('', include('store.urls')),  # <-- includes the app URLs
]
