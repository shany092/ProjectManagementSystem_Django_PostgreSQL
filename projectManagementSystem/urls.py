from django.urls import path
from django.contrib.auth import views as auth_views
from pmpapp import views
from django.contrib import admin
from pmpapp.admin import admin_site  # Use custom admin site


urlpatterns = [
    # Admin-specific routes
    path("admin/", admin_site.urls),  # Django Admin
    path("admin/dashboard/", views.admin_dashboard, name="admin-dashboard"),
    # ajax to load county, city and state according to the selected continent or country
    path('ajax/load-countries/', views.load_countries, name='ajax_load_countries'),
    path('ajax/load-states/', views.load_states, name='ajax_load_states'),
    path('ajax/load-cities/', views.load_cities, name='ajax_load_cities'),
    path('ajax/next-code/', views.get_next_employee_code, name='next_employee_code'),

    # Employee-specific routes
    path("employee/login/", views.CustomLoginView.as_view(), name="employee-login"),
    path("employee/dashboard/", views.employee_dashboard, name="employee-dashboard"),

    # Default password management (Optional)
    path("password_reset/", auth_views.PasswordResetView.as_view(), name="password_reset"),
    path("password_reset_done/", auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
]



# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)