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
from django.http import JsonResponse
from django.urls import path, include
from django.shortcuts import redirect


def redirect_admin(request):
    return redirect('admin_access')


def healthcheck(request):
    return JsonResponse({'ok': True})

urlpatterns = [
    path('admin/', redirect_admin),
    path('health/', healthcheck, name='healthcheck'),
    path('', include('store.urls')),  # <-- includes the app URLs
]
