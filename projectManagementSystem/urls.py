from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from pmpapp import views

from django.urls import path
from pmpapp.views import EmployeeLoginView, employee_dashboard

urlpatterns = [
     path('admin/', admin.site.urls),
    # path('', include('pmpapp.urls')),
    path('login/', EmployeeLoginView.as_view(), name='employee-login'),
    path('dashboard/', employee_dashboard, name='employee-dashboard'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)