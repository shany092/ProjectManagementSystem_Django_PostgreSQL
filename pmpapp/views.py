from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.contrib.auth.views import  LoginView
from django.contrib.auth.decorators import login_required
from .models import Country, State, City, Employee, EmployeeType, EmployeeCodeRule
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Max


# def employee_dashboard(request):
#     """
#     Employee Dashboard
#     """
#     return render(request, 'employee/dashboard.html', {'employee': request.user})

def is_admin(user):
    return user.is_staff or user.is_superuser

class CustomLoginView(LoginView):
    """
    Handles login and redirects based on the user's role.
    """
    template_name = 'employee/login.html'

    def form_valid(self, form):
        """
        Redirect user based on role after successful login.
        """
        user = form.get_user()
        login(self.request, user)
        if is_admin(user):
            return redirect('/admin/')  # Admin Dashboard
        return redirect('/employee/dashboard/')  # Employee Dashboard

@staff_member_required
def admin_dashboard(request):
    """
    Admin Dashboard for superusers.
    """
    return render(request, "admin/index.html")


@login_required
def employee_dashboard(request):
    """
    Employee Dashboard for regular employees.
    """
    return render(request, 'employee/dashboard.html', {'employee': request.user})
# def next_employee_code(request):
#     """
#     Dynamically calculate and provide the next employee code based on the prefix.
#     """
#     prefix = request.GET.get('prefix', '').strip()
#     if not prefix:
#         return JsonResponse({'error': 'Invalid prefix'}, status=400)

#     try:
#         last_code = Employee.objects.filter(employee_code__startswith=prefix).order_by('-employee_code').first()
#         next_number = int(last_code.employee_code[-4:]) + 1 if last_code else 1
#         next_code = f"{prefix}{next_number:04d}"
#         return JsonResponse({'next_code': next_code})
#     except Exception as e:
#         return JsonResponse({'error': f"Unable to fetch employee code. Error: {str(e)}"}, status=500)
# view to filter employee type on country base
def filter_employee_types(request):
    """
    Filters employee types based on the selected country and returns them as JSON.
    """
    country_id = request.GET.get('country')  # Get the selected country's ID
    if not country_id:  # If no country is provided, return an empty response
        return JsonResponse([], safe=False)
    
    # Filter the EmployeeType objects by country
    employee_types = EmployeeType.objects.filter(country_id=country_id).values('id', 'name')
    
    # Return the filtered data as a JSON response
    return JsonResponse(list(employee_types), safe=False)
# Fetch the next available Employee Code
def get_next_employee_code(request):
    prefix = request.GET.get('prefix', '')
    if prefix:
        # Query to determine next code
        last_code = Employee.objects.filter(employee_code__startswith=prefix).aggregate(
            Max('employee_code'))['employee_code__max']
        next_number = int(last_code[-4:]) + 1 if last_code else 1
        next_code = f"{prefix}{next_number:04}"
        return JsonResponse({'next_code': next_code})
    return JsonResponse({'error': 'Invalid prefix'}, status=400)
def load_countries(request):
    continent_id = request.GET.get('continent_id')
    countries = Country.objects.filter(continent_id=continent_id).values('id', 'name')
    return JsonResponse(list(countries), safe=False)

def load_states(request):
    country_id = request.GET.get('country_id')
    states = State.objects.filter(country_id=country_id).values('id', 'name')
    return JsonResponse(list(states), safe=False)

def load_cities(request):
    state_id = request.GET.get('state_id')
    cities = City.objects.filter(state_id=state_id).values('id', 'name')
    return JsonResponse(list(cities), safe=False)
def get_states(request):
    country_id = request.GET.get('country')
    states = State.objects.filter(country_id=country_id).values('id', 'state_name')
    return JsonResponse({s['id']: s['state_name'] for s in states})

def get_cities(request):
    country_id = request.GET.get('country')
    cities = City.objects.filter(country_id=country_id).values('id', 'city_name')
    return JsonResponse({c['id']: c['city_name'] for c in cities})

def get_employee_types(request):
    country_id = request.GET.get('country')
    employee_types = EmployeeType.objects.filter(country_id=country_id).values('id', 'name')
    return JsonResponse({e['id']: e['name'] for e in employee_types})

def get_country_mask(request, country_id):
    country = Country.objects.filter(pk=country_id).first()
    return JsonResponse({'phone_number_mask': country.phone_number_mask,
                         'cnic_number_mask': country.cnic_number_mask if country else ''}
            )
