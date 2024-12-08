# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import AllowAny
# from rest_framework_simplejwt.tokens import RefreshToken
# from rest_framework import status
# from .serializers import EmployeeSerializer
# from rest_framework import viewsets
import datetime
from django.utils import timezone
from django.db.models.manager import BaseManager
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from django.http import JsonResponse
from django.urls import reverse
from datetime import datetime 
from .models import Continent, Country, State, City, Designation, Department, Employee

from django.contrib.auth.views import LoginView
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

class EmployeeLoginView(LoginView):
    template_name = 'employee/login.html'

@login_required
def employee_dashboard(request):
    return render(request, 'employee/dashboard.html', {'employee': request.user})


