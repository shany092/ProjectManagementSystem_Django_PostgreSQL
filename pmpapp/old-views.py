import datetime
# from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import HttpResponse
from django.utils import timezone
from django.db.models.manager import BaseManager
from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.admin.views.decorators import staff_member_required
# from django.conf import settings
# from django.http import JsonResponse
# from django.urls import reverse
# from datetime import datetime 
from .models import Continent, Country, State, City, Designation, Department, Employee
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import  LoginView
from pmpapp.forms import EmailAuthenticationForm

# @staff_member_required
def dashboard(request):
    

    # Render the dashboard with the attendance calendar data
    return render(request, 'index.html'
                #   , 
                #   {    }
                )



class EmployeeLoginView(LoginView):
    def login_view(request):
        if request.method == "POST":
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('employee/dashboard.html')  # Replace with the desired dashboard
            else:
                messages.error(request, "Invalid email or password.")
        return render(request, 'login.html')


def employee_dashboard(request):
    return render(request, 'employee/dashboard.html', {'employee': request.user})

from django.contrib.auth import authenticate, login

def employee_login(request):
    email = request.POST['email']
    password = request.POST['password']

    # Authenticate against the CustomUser model
    user = authenticate(request, email=email, password=password)
    if user is not None:
        login(request, user)
        return HttpResponse("Login successful")
    else:
        return HttpResponse("Invalid credentials")

# @staff_member_required
def employee_change_view(request, employee_id):
    # Fetch the employee instance or return a 404 if not found
    employee = get_object_or_404(Employee, id=employee_id)
    
    # Render a template with employee data
    context = {
        'employee': employee
    }
    return render(request, 'admin/employee_change.html', context)


