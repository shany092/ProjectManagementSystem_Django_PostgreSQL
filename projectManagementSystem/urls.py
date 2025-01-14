from django.urls import path
from django.contrib.auth import views as auth_views
from pmpapp import views
from pmpapp.views import CustomLoginView, employee_dashboard
from django.contrib import admin
from pmpapp.admin import admin_site  # Use custom admin site


urlpatterns = [
     # Custom admin login to replace default
    path("admin/login/", CustomLoginView.as_view(), name="employee-login"),
    path("employee/dashboard/", employee_dashboard, name="employee-dashboard"),
    # path('tasks/', views.task_list, name='task_list'),
    # path('tasks/<int:task_id>/', views.task_detail, name='task_detail'),
    # Admin-specific routes
    path("admin/", admin_site.urls),  # Django Admin
    path("admin/dashboard/", views.admin_dashboard, name="admin-dashboard"),
    # ajax to load county, city and state according to the selected continent or country
    path('api/states/', views.get_states, name='api_get_states'),
    path('api/get_states/', views.get_states, name='api_get_states'),

    path('api/cities/', views.get_cities, name='api_get_cities'),
    path('api/employee_types/', views.get_employee_types, name='api_get_employee_types'),
    # path('api/get_employee_types/', views.get_employee_types, name='api_get_employee_types'),
    
    path('api/get_country_data/<int:country_id>/', views.get_country_data, name='get_country_data'),
    path('api/get_state_data/<int:country_id>/<int:state_id>/', views.get_state_data, name='get_state_data'),

    # path('ajax/load-countries/', views.load_countries, name='ajax_load_countries'),
    # path('ajax/load-states/', views.load_states, name='ajax_load_states'),
    # path('ajax/load-cities/', views.load_cities, name='ajax_load_cities'),
    # path('ajax/next-code/', views.get_next_employee_code, name='next_employee_code'),
    # path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),
    # path('employee/dashboard/', views.employee_dashboard, name='employee_dashboard'),
    
    # Employee-specific routes
    # path("admin/login/", views.CustomLoginView.as_view(), name="employee-login"),

    # path("employee/dashboard/", views.employee_dashboard, name="employee-dashboard"),


    # Default password management (Optional)
    path("password_reset/", auth_views.PasswordResetView.as_view(), name="password_reset"),
    path("password_reset_done/", auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
]



# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)