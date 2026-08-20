from django.urls import path, include
from store import views

urlpatterns = [
    # Google OAuth / Social Auth
    path('auth/', include('social_django.urls', namespace='social')),

    # Custom Admin Dashboard
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('admin_panel/', views.admin_control_center, name='admin_control_center'),
    path('admin-access/', views.admin_access, name='admin_access'),
    
    # Store URLs
    path('', include('store.urls')),
]
