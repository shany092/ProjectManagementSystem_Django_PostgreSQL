from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden
import traceback
from django.contrib.auth import authenticate, login, get_user_model #, GROUP_MODULES
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.contrib.auth.views import  LoginView
from django.contrib.auth.decorators import login_required,user_passes_test, permission_required
from .models import Country, State, City, Employee, EmployeeType, EmployeeCodeRule
from .models import Task, Project, Clients
from pmpapp.forms import SubTaskForm, TaskForm
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Max
from django.conf import settings

# from django.contrib import GROUP_MODULES
from django.contrib.auth.models import Group

CustomUser = get_user_model()



@login_required
def employee_dashboard(request):
    """
    Employee Dashboard
    """
    CustomUser = request.user
    team_members=Task.objects.filter(team_members=CustomUser)
    assigned_tasks =team_members  #(team_members=employee)
    # Get the groups of the logged-in user
    # user_groups = CustomUser.groups.all()
    user_permissions = CustomUser.get_all_permissions()
    user_groups = CustomUser.groups.all()
    # user_groups = request.user.groups.values_list('name', flat=True)
    # Optionally, fetch additional data such as projects
    projects = Project.objects.filter(team_members=CustomUser)  # Adjust this to your model fields
  
    # Remove duplicates in case of multiple group memberships
    # accessible_modules = list(set(accessible_modules))
    # employee = request.user.employee_profile
    # assigned_tasks = Task.objects.filter(team_members=employee)

    # return render(request, 'employee/dashboard.html', {'employee': request.user})
    # Define group-to-modules mapping (customize for your setup)
   
    return render(request, 'employee/dashboard.html',  { # 'employee-admin', 
        'employee': CustomUser,
        'user_permissions': user_permissions,
        'assigned_tasks': assigned_tasks,
        # 'accessible_modules': accessible_modules,
        'groups': user_groups,
        'projects': projects,
    })

# def is_admin(user):
#     return user.is_staff or user.is_superuser

class CustomLoginView(LoginView):
    """
    Handles login and redirects based on the user's role.
    """
    template_name = 'admin/login.html'

    def form_valid(self, form):
        """
        Redirect user based on role after successful login.
        """
        user = form.get_user()
        login(self.request, user)

        if user.is_superuser:
            return redirect('/admin/')  # Superuser goes to Admin Dashboard
        # elif user.is_staff:
        #     return redirect('/staff/dashboard/')  # Staff members see a specific dashboard
        else:
            # user.groups.filter(name="Employee").exists()
            return redirect('/employee/dashboard')  # Regular employees see their dashboard

class CustomLoginView(LoginView):
    """
    Handles login and redirects based on the user's role.
    """
    template_name = 'admin/login.html'

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)  # Log the user in
        
        # Redirect users based on their roles
        if user.is_superuser:
            return redirect('/admin/')  # Superuser: Admin dashboard
        # elif user.is_staff:
        #     return redirect('/employee/dashboard.html')  # Employee: Custom dashboard
        return redirect('/employee/dashboard')  # Default redirect for other users
    #------------------------------------------------------

@staff_member_required
def admin_dashboard(request):
    """
    Admin Dashboard for superusers.
    """
    return render(request, "admin/index.html")

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
    if country_id:
        # Use the correct primary key and name field
        state = State.objects.filter(country_id=country_id).values('state_id', 'state_name')
        return JsonResponse(list(state), safe=False)
    return JsonResponse([], safe=False)  # Return an empty array if no country is provided
# in case of get_states not working use the below fuction and comment the above function
# def get_states(request):
#     country_id = request.GET.get('country')
#     if country_id:
#         state = State.objects.filter(country_id=country_id)
#         return JsonResponse({s.state_id: s.state_name for s in state})
#     return JsonResponse({})

def get_cities(request):
    country_id = request.GET.get('country')
    cities = City.objects.filter(country_id=country_id).values('id', 'city_name')
    return JsonResponse({c['id']: c['city_name'] for c in cities})

def get_employee_types(request):
    country_id = request.GET.get('country')
    if country_id:
        employee_types = EmployeeType.objects.filter(country_id=country_id).values('id', 'name')
        return JsonResponse(list(employee_types), safe=False)
    # return JsonResponse([], safe=False)
    return JsonResponse({e['id']: e['name'] for e in employee_types})

def get_country_data(request, country_id):
    if country_id:
        country = Country.objects.filter(pk=country_id).first()
        employee_types = EmployeeType.objects.filter(country_id=country_id).values('id', 'name')
        state = State.objects.filter(country_id=country_id).filter(country_id=country_id).values('state_id', 'state_name')
        city = City.objects.filter(country_id=country_id).filter(country_id=country_id).values('city_id', 'city_name')


        response_data  = {
            'state_select': list(state),
            'select_city': list(city),
            'emp_types': list(employee_types),  # Convert QuerySet to list for JSON serialization
            'masks_list': {
                'phone_number_mask': country.phone_number_mask if country else '',
                'cnic_number_mask': country.cnic_number_mask if country else '',
            }
        }
        return JsonResponse(response_data)
    response_data ={
        'emp_types':[], 'state_select':[], 'select_city': [], 
        'masks_list':{'phone_number_mask': '', 'cnic_number_mask': ''}
    }
    # print(response_data)
    return JsonResponse(response_data)

def get_state_data(request, country_id, state_id):
    if country_id and state_id:
        city = City.objects.filter(country_id=country_id).filter(state_id=state_id).values('city_id', 'city_name')
        response_data  = {
            'city_select': list(city)
            }
        return JsonResponse(response_data)
    response_data ={
        'city_select':[],
    }
    print(response_data)
    return JsonResponse(response_data)

def debug_view(request):
    try:
        # Intentionally cause an error for demonstration
        x = 1 / 0
    except Exception as e:
        error_message = f"<h1>Error Occurred</h1><pre>{traceback.format_exc()}</pre>"
        return HttpResponse(error_message, content_type="text/html")

@login_required
def assigned_tasks_view(request):
    employee = request.user
    assigned_tasks = Task.objects.filter(team_members=employee)

    if request.method == 'POST':
        form = SubTaskForm(request.POST, user=request.user)
        if form.is_valid():
            task = form.cleaned_data['task']
            parent_task = form.cleaned_data['task']
            if task not in assigned_tasks and parent_task not in assigned_tasks:
                return HttpResponseForbidden("You cannot add subtasks to a task not assigned to you.")
            
            subtask = form.save(commit=False)
            subtask.project = form.cleaned_data['parent_task'].project  # Inherit the project from the parent task
            subtask.parent_task = form.cleaned_data['parent_task']
            subtask.save()
            form.save_m2m()  # Save M2M relationships
            return redirect('assigned_tasks')  # Redirect to the assigned tasks view
    else:
        form = SubTaskForm(request.POST or None, user=request.user)

    return render(request, 'employee/assigned_tasks.html', {
        'assigned_tasks': assigned_tasks,
        'form': form,
    })  

# @login_required
# def assigned_tasks_view(request):
#     employee = request.user
#     assigned_tasks = Task.objects.filter(team_members=employee)

#     if request.method == 'POST':
#         form = SubTaskForm(request.POST, user=request.user)
#         if form.is_valid():
#             task = form.cleaned_data['task']
#             if task not in assigned_tasks:
#                 return HttpResponseForbidden("You cannot add subtasks to a task not assigned to you.")
            
#             subtask = form.save(commit=False)
#             subtask.project = form.cleaned_data['task'].project  # Inherit the project from the parent task
#             subtask.parent_task = form.cleaned_data['task']
#             subtask.save()
#             form.save_m2m()  # Save M2M relationships
#             return redirect('assigned_tasks')  # Redirect to the assigned tasks view
#     else:
#         form = SubTaskForm(request.POST or None, user=request.user)

#     return render(request, 'employee/assigned_tasks.html', {
#         'assigned_tasks': assigned_tasks,
#         'form': form,
#     })  

@login_required
def project_tasks_view(request, project_id):
    tasks = Task.objects.filter(project_id=project_id, parent_task=None)  # Root tasks under a project
    return render(request, 'tasks/accordion_view.html', {'tasks': tasks})

@login_required
def employee_task_list(request):
    """
    View to list all tasks and subtasks assigned to the logged-in user.
    """
    user = request.user  # Get the currently logged-in user

    # Fetch tasks where the current user is in the team_members ManyToMany field
    tasks = Task.objects.filter(team_members=user).distinct()
    # templates\employee\tasks\task_list.html
    return render(request, 'employee/tasks/task_list.html', {'tasks': tasks})

@login_required
def employee_add_subtask(request, task_id):
    parent_task = get_object_or_404(Task, pk=task_id, team_members=request.user)  # Ensure parent is assigned to the user

    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            sub_task = form.save(commit=False)
            sub_task.parent_task = parent_task  # Set parent task
            sub_task.project = parent_task.project  # Inherit project
            sub_task.save()  # Save the sub-task to assign it an ID
            
            # Assign team member after saving
            sub_task.team_members.set([request.user])
            
            return redirect('employee_task_list')  # Redirect after successful save
    else:
        form = TaskForm()

    return render(request, 'employee/tasks/add_subtask.html', {
        'form': form,
        'parent_task': parent_task,
    })

# @login_required
# def task_detail(request, id):
#     # Fetch the task by its ID or return a 404 if not found
#     task = get_object_or_404(Task, id=id)
    
#     # Pass the task details to the template
#     return render(request, 'employee/task_list.html', {'task': task})

def group_detail(request, id):
    group = get_object_or_404(Group, id=id)
    return render(request, 'group_detail.html', {'group': group})

def project_detail(request, id):
    project = get_object_or_404(Project, id=id)
    return render(request, 'project_detail.html', {'project': project})