from django import forms
from django.db.models import Max
from .forms import TaskAdminForm
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib import messages
from django.utils.html import format_html

from django.urls import reverse
from django.templatetags.static import static
from django.utils.safestring import mark_safe
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.utils.functional import cached_property
from django.contrib.auth.models import Group, Permission
from django.contrib.admin import AdminSite
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from pmpapp.models import Project, Task, Team, TeamMember, Comment, ProjectTeam, Clients
from pmpapp.models import  EmployeeType, EmployeeCodeRule, Employee, ProjectType
#, ProjectInterval
from pmpapp.models import Department, Designation, CustomUser, City, Continent, Country, State
from django.http import HttpResponseRedirect
# Custom AdminSite
class MyCustomAdminSite(AdminSite):
    """
    Customized admin site to restrict model visibility.
    """
    admin.site.site_header = "Mekex | Innovation"
    admin.site.site_title = "MKX"
    admin.site.index_title = "Mekex Innovation"

    def has_permission(self, request):
        """
        Only active superusers can access the admin site.
        """
        return request.user.is_active and request.user.is_superuser

    
    def dashboard_view(self, request):
        """
        Custom dashboard view.
        """
        if not request.user.is_superuser:
            return redirect('/employee/dashboard/')
        return render(request, "index.html")

    def get_urls(self):
            """
            Add custom dashboard URL.
            """
            urls = super().get_urls()
            custom_urls = [
                path('dashboard/', self.admin_view(self.dashboard_view), name="custom_dashboard"),
            ]
            return custom_urls + urls

admin_site = MyCustomAdminSite(name="mypmpadmin")

# Custom UserAdmin
@admin.register(CustomUser, site=admin_site)  # Register with the custom admin site
class CustomUserAdmin(UserAdmin):
    model = CustomUser

    # Restrict editing of certain fields
    readonly_fields = ('username', 'is_active', 'is_staff', 'date_joined', 'email', 'first_name', 'last_name')

    fieldsets = (
        ('User Info', {'fields': ('email', 'username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups')}),  # Adjust 'user_permissions' if required
        ('Important Dates', {'fields': ('date_joined',)}),
    )

    def has_add_permission(self, request):
        """
        Prevent adding new users.
        """
        return False

    def has_delete_permission(self, request, obj=None):
        """
        Prevent deleting users.
        """
        return False

    def has_change_permission(self, request, obj=None):
        """
        Allow permission changes only.
        """
        if obj:
            return True  # Allow changes for specific users
        return True  # Allow listing

    def get_form(self, request, obj=None, **kwargs):
        """
        Modify form to restrict permission edits.
        """
        form = super().get_form(request, obj, **kwargs)
        if 'user_permissions' in form.base_fields:
            form.base_fields.pop('user_permissions')  # Hide permissions
        for field_name, field in form.base_fields.items():
            if field_name not in ['groups']:  # Make all but 'groups' read-only
                field.disabled = True
        return form

# Employee Admin
class EmployeeAdminForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Determine filtering for employee_type based on the request data or existing instance
        if 'country' in self.data:
            try:
                country_id = int(self.data.get('country'))
                self.fields['employee_type'].queryset = EmployeeType.objects.filter(country_id=country_id)
                self.fields['state'].queryset = State.objects.filter(country_id=country_id)
                self.fields['city'].queryset = City.objects.filter(country_id=country_id)

            except (ValueError, TypeError):
                self.fields['employee_type'].queryset = EmployeeType.objects.none()
                self.fields['state'].queryset         = State.objects.none()
                self.fields['city'].queryset          = City.objects.none()

        elif self.instance and self.instance.pk:
             self.fields['employee_type'].queryset = EmployeeType.objects.filter(country=self.instance.country)
             self.fields['state'].queryset =  State.objects.filter(country=self.instance.country)
             self.fields['city'].queryset =  City.objects.filter(country=self.instance.country)

        else:
            self.fields['employee_type'].queryset = EmployeeType.objects.none()
            self.fields['state'].queryset = State.objects.none()
            self.fields['city'].queryset = City.objects.none()
        # self.fields['continent'].widget.attrs.update({
        # 'id': 'idd_continent'
        # })
        # Set up dynamic masking for fields
        self.fields['phone_number'].widget.attrs.update({
            'class': 'phone-input'
        })
        self.fields['nic_number'].widget.attrs.update({
            'class': 'nic_number-input'
        })

@admin.register(Employee, site=admin_site)
class EmployeeAdmin(admin.ModelAdmin):
    # class Media:
    #    js = (
    #         # "admin/js/jquery.min.js",
    #         # 'admin/js/jquery.mask.js',
    #         # "admin/js/mask.min.js",
    #         "admin/js/employee_dynamic_filtering.js"
    #        )

    form = EmployeeAdminForm
    list_display = ( 'employee_code', 'first_name', 'last_name', 'email', 'employee_type', 'is_active')
    search_fields = ('first_name', 'last_name', 'email', 'employee_code')
    list_filter = ('employee_type', 'is_active', 'created_at')
    readonly_fields = ('employee_code',)  # Ensure employee_code is auto-generated
    exclude = ('CustomUser','continent')  # Remove the user field from the form

    fieldsets = (
        (None, {
            'fields': (
                'country',
                'employee_type',
                'employee_code',
                'first_name',
                'last_name',
                'email',
                'phone_number',
                'nic_number',
                'passport_number',
            )
        }),
        ('Job Details', {
            'fields': (
                'job_title',
                'department',
                'designation',
                # 'continent',
                
                'state',
                'city',
                'salary',
                'date_joined',
                'left_date'
            )
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser')
        }),
    )

    def save_model(self, request, obj, form, change):

        """
        Automatically create and associate a new user when saving a new employee.
        """
        # Save the Employee object first without the user (deferred relationship creation)
        is_new = obj.pk is None
        super().save_model(request, obj, form, change)

        if is_new and not obj.user:
            # Create the CustomUser instance
            CustomUser = get_user_model()
            username = f"{obj.first_name.lower()}_{obj.last_name.lower()}_{obj.pk}"  # Ensure unique username
            email = obj.email
            user = CustomUser.objects.create_user(username=username, email=email, password=None)
            
            # Associate the newly created user with the Employee instance
            obj.user = user
            obj.save()  # Update the Employee instance with the user association

class BaseLocationAdmin(admin.ModelAdmin):
    search_fields = ('name',)

class EmployeeTypeForm(forms.ModelForm):
    class Meta:
        model = EmployeeType
        fields = '__all__'  # Include both 'name' and 'country'
    
    def clean_country(self):
        country = self.cleaned_data.get('country')
        if not country:
            raise forms.ValidationError("You must select a country.")
        return country

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # You can add further customizations here if needed

@admin.register(EmployeeType, site=admin_site)
class EmpType(BaseLocationAdmin):
    list_display = ('name', 'country')
    form = EmployeeTypeForm  # Use the custom form

    # To filter the displayed employee types based on selected country in admin
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs  # Return all records for superusers
        # Custom filter logic if necessary
        return qs

    # Optionally, include inline filters to easily find employee types by country
    list_filter = ('country',)

class EmployeeCodeRuleForm(forms.ModelForm):
    class Meta:
        model = EmployeeCodeRule
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply the filtering logic only if adding a new EmployeeCodeRule
        if not self.instance.pk:  # Check if it's a new instance (add mode)
            used_employee_types = EmployeeCodeRule.objects.values_list('employee_type', flat=True)
            self.fields['employee_type'].queryset = EmployeeType.objects.exclude(pk__in=used_employee_types)

@admin.register(EmployeeCodeRule, site=admin_site)
class EmpCodeRule(BaseLocationAdmin):
    list_display = ('code_prefix', 'starting_number', 'employee_type') #, 'get_employee_type_name')
    form = EmployeeCodeRuleForm
    # To display the employee type name in listing
    # def get_employee_type_name(self, obj):
    #     return obj.employee_type.name if obj.employee_type else "-"
    # get_employee_type_name.short_description = 'Employee Type'

# -------------------------------HiddenAdmin------------------------------------------------# 
   
# Customization to hide models from the sidebar menu
class HiddenAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        # Return False to hide this model from the sidebar menu
        return False

# Project Admin
class TaskInline(admin.TabularInline):  # TabularInline provides a table-like inline view
    model = Task
    fields = ('task_name', 'team_members', 'due_date', 'priority', 'status')  # Fields to show inline
    show_change_link = True  # Add a link to edit the task directly
    extra = 1  # Number of empty forms to display

# from django.contrib.admin import TabularInline

# class EmployeeInline(admin.TabularInline):
#     model = Project.team_members.through
#     extra = 1  # Number of additional rows for new members
#     verbose_name = "Team Member"
#     verbose_name_plural = "Team Members"

class SubTaskInline(admin.TabularInline):
    model = Task
    fk_name = 'parent_task'
    project_id = 'project_id'
    extra = 1
    exclude = ('project','team_members')
    # fields = ('task_name', 'due_date', 'priority', 'status', 'team_members')


# ------------------------------- Project part ----------------------------

@admin.register(ProjectType, site=admin_site)
class ProjectTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'abbreviation')

# @admin.register(ProjectInterval, site=admin_site)
# class ProjectIntervalAdmin(admin.ModelAdmin):
    # list_display = ('name', 'interval')

import logging

logger = logging.getLogger(__name__)
class ProjectAdminForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        project_type = cleaned_data.get("project_type")
        if not project_type:
            raise forms.ValidationError("Project Type is required!")
        return cleaned_data


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['Client_ID'].help_text = "Select a Client_ID from the dropdown"
    def clean_Client_ID(self):
        Client_ID = self.cleaned_data.get('Client_ID')
        print(f"Cleaning Client_ID: {Client_ID}")  # Debug log
        if Client_ID == '3-CLIE-PALA':  # Replace with your validation rule
            raise forms.ValidationError("Client_ID cannot be '3-CLIE-PALA'.")
        return Client_ID

    def clean_Project_number(self):
        project_number = self.cleaned_data.get('Project_number')
        print(f"Cleaning Project_number: {project_number}")  # Debug log
        if project_number and project_number < 600:  # Example validation rule
            raise forms.ValidationError("Project number must be 600 or higher.")
        return project_number
   
    # def __init__(self, *args, **kwargs):
        
    #     try:
    #         super().__init__(*args, **kwargs)  # Call the parent's __init__ method
    #         # Dynamically show the next available project number in the info section
    #         next_project_number = Project.objects.aggregate(Max('Project_number'))['Project_number__max'] or 599
    #         next_project_number += 1
    #         self.fields['Project_number'].help_text = f"The next available Project Number is {next_project_number}."
    #     except Exception as e:
    #         print(f"An error occurred in Project AdminForm initialization: {str(e)}")
        #     # Dynamically show the next available project number in the info section
        # max_project_number = Project.objects.aggregate(Max('Project_number')).get('Project_number__max', 599)
        # # Handle case when max_project_number is None
        # next_project_number = (max_project_number or 599) + 1
        # self.fields['Project_number'].help_text = f"The next available Project Number is {next_project_number}."

@admin.register(Project, site=admin_site)
class ProjectAdmin(admin.ModelAdmin):
    form = ProjectAdminForm
    
    list_display = ('project_name','Client_ID', 'project_id', 'Project_number', 'start_date', 'end_date', 'status', 'add_task_link')# , 'created_by' 
    # filter_horizontal = ('team_members',)
    fields = ('Client_ID', 'project_type', 'project_name', 
              'description', 'start_date', 'end_date', 'status') #, 'team_members', 'project_interval'
    search_fields = ('project_name', 'Project_number', 'Client_ID') #, 'Client_Name'
    list_filter = ('status', 'start_date', 'end_date') # , 'created_by'
    inlines = [TaskInline] # [a,b]
    def add_task_link(self, obj):
        """Generate a dynamic URL for adding a task to the project."""
        url = reverse('admin:pmpapp_task_add') + f'?project={obj.id}'
        return format_html('<a href="{}">Add Task</a>', url)
    add_task_link.short_description = 'Actions'
    # exclude= ('created_by', 'interval', 'project','parent_task','team_members') 

    # def save_model(self, request, obj, form, change):
    #     try:
    #         if form.is_valid():
    #             super().save_model(request, obj, form, change)
    #         else:
    #             # Log errors to console
    #             print("Form validation errors:", form.errors.as_json())
    #     except Exception as e:
    #         import traceback
    #         traceback.print_exc()  # Print the full error traceback for debugging

    #     print(form.errors)
    
    def save(self, *args, **kwargs):
        if not self.Project_number:
            self.Project_number = self.get_next_project_number()
        if not self.pk:  # Ensure this block runs only on object creation
            type_code = self.project_type.abbreviation if self.project_type else "XX"
            # interval_code = str(self.project_interval.interval) if self.project_interval else "00"
            self.project_id = f"{self.Project_number}-{type_code}"
            #-{interval_code}

        # Intentionally trigger an error for testing (example)
        # if not type_code:
        #     raise Exception("Project Type code is not properly set!")
        
        super().save(*args, **kwargs)

    # def get_form(self, request, obj=None, **kwargs):
    #     form = super().get_form(request, obj, **kwargs)
        
    #     # Dynamically override the project number help text
    #     max_project_number = Project.objects.aggregate(Max('Project_number')).get('Project_number__max', 599)
    #     next_project_number = (max_project_number or 599) + 1
    #     form.base_fields['Project_number'].help_text = f"The next available Project Number is {next_project_number}."
    #     return form

class TaskAdminForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = '__all__'
    
    exclude = ('project','parent_task')

    def _init_(self, *args, request=None, **kwargs):
        super()._init_(*args, **kwargs)

        # Ensure parent_task queryset is limited to tasks in the same project
        if self.instance and self.instance.pk:
            # Editing an existing task
            self.fields['parent_task'].queryset = Task.objects.filter(project=self.instance.project)
        else:
            # Adding a new task
            self.fields['parent_task'].queryset = Task.objects.none()

        if request:
            parent_task_id = request.GET.get('parent_task')
            project_id = request.GET.get('project')

            if parent_task_id:
                # Adding a subtask under an existing task
                try:
                    parent_task = Task.objects.get(pk=parent_task_id)
                    self.instance.parent_task = parent_task
                    self.instance.project = parent_task.project
                    self.fields['project'].widget = forms.HiddenInput()
                    self.fields['parent_task'].queryset = Task.objects.filter(project=parent_task.project)
                except Task.DoesNotExist:
                    pass
            elif project_id:
            # Adding a task directly to a project
                try:
                    project = Project.objects.get(pk=project_id)
                    self.instance.project = project
                    # self.fields['project'].widget = forms.HiddenInput()
                    self.fields['parent_task'].queryset = Task.objects.filter(project=project)
                except Project.DoesNotExist:
                    pass
@admin.register(Task, site=admin_site)
class TaskAdmin(admin.ModelAdmin):
    form = TaskAdminForm
    list_display = ('custom_change_link', 'task_name', 'project', 'due_date', 'priority', 'status', 'parent_task') #, 'add_subtask_link' ,'display_team_members'
    search_fields = ('task_name', 'project__project_name')
    list_filter = ('priority', 'status', 'due_date')
    # filter_horizontal = ('team_members',)  # Enable multi-select for team members
    # filter_vertical = ('team_members',)
    # exclude = ('project',)
    raw_id_fields = ('parent_task',)
    # exclude = ('project','parent_task')
    inlines = [SubTaskInline]

    def add_view(self, request, object_id=None, form_url='', extra_context=None):
        """Override to pre-fill project or parent task."""
        if object_id:
            try:
                parent_task = Task.objects.get(pk=object_id)
                # Redirect to the add form with the parent task set
                return redirect(f"{reverse('admin:pmpapp_task_add')}?parent_task={parent_task.id}")
            except Task.DoesNotExist:
                pass
        return super().add_view(request, form_url, extra_context)
    
    def custom_change_link(self, obj):
        """
        Create a custom change link that includes project and parent_task as query parameters.
        """
        # Get the project and parent_task related to the task
        project_id = obj.project.id if obj.project else None
        parent_task_id = obj.parent_task.id if obj.parent_task else None
        
        # Construct the URL for the change view with query parameters
        change_url = reverse('admin:pmpapp_task_change', args=[obj.pk])
        
        # Add the project and parent_task as query parameters to the URL
        query_params = []
        if project_id:
            query_params.append(f'project={project_id}')
        if parent_task_id:
            query_params.append(f'parent_task={parent_task_id}')
        
        # If there are query parameters, append them to the URL
        if query_params:
            change_url += '?' + '&'.join(query_params)
        
        # Return the formatted HTML link
        return format_html('<a href="{}">Change</a>', change_url)
    
    # def add_subtask_link(self, obj):
    #     """Generate a dynamic URL for adding a subtask under this task."""
    #     url = reverse('admin:pmpapp_task_add') + f'?project={obj.project.id}&parent_task={obj.id}'
    #     return format_html('<a href="{}">Add Subtask</a>', url)
    # add_subtask_link.short_description = 'Actions'
    # def save_model(self, request, obj, form, change):
    #     """Set project for new tasks before saving."""
    #     # if not obj.pk:  # New task
    #     project_id = request.GET.get('project')
    #     if project_id:
    #         obj.project = Project.objects.get(pk=project_id)
    #         # obj.project_id= project_id
    #     super().save_model(request, obj, form, change)
    # def save(self, commit=True):
    #     if not self.instance.project and self.instance.parent_task:
    #         parent_task = Task.objects.get(pk=self.instance.parent_task)
    #         self.instance.project = parent_task.project
        
    #     return super().save(commit=commit)

    # def save_model(self, request, obj, form, change):
    #     """Ensure the project is correctly assigned when saving."""
    #     if not obj.project and obj.parent_task:
    #         parent_task = Task.objects.get(pk=obj.parent_task)
    #         obj.project = parent_task.project
    #     elif request:
    #         project_id = request.GET.get('project')
    #         obj.project = Project.objects.get(pk=project_id)
    #     else:
    #         obj.project = Project.objects.get(pk=request.project)
    #         obj.project = request.project
    #     super().save_model(request, obj, form, change)
    def get_task_id_from_url(self, request):
        """Extract the task ID from the URL path."""
        path = request.path
        parts = path.split('/')
        task_id = parts[4]
        return task_id
    def get_form(self, request, obj=None, **kwargs):
        """Inject query parameters into the form."""
        form = super().get_form(request, obj, **kwargs)

        # Read query parameters
        project_id = request.GET.get('project')
        parent_task_id = request.GET.get('parent_task')

        # Attach query parameters to the form instance
        form.request = request
        form.project_id = project_id
        form.parent_task_id = parent_task_id

        return form
    
    # def get_form(self, request, obj=None, **kwargs):
    #     form_class = super().get_form(request, obj, **kwargs)  # Get the form class
    #     # Override the form's _init_ to pass the request
    #     class FormWithRequest(form_class):
    #         def _init_(self, *args, **form_kwargs):
    #             form_kwargs['request'] = request
    #             super()._init_(*args, **form_kwargs)
        
    #     return FormWithRequest
    #  # def get_form(self, request, obj=None, **kwargs):
    # 
        #     form = super().get_form(request, obj, **kwargs)
    #     form.request = request  # Pass the request to the form
    #     return form
    # def save_model(self, request, obj, form, change):
    #     if not obj.pk:  # If the object is new
    #         obj.project = form.initial.get('project')  # Set the project from the initial data
    #     super().save_model(request, obj, form, change)
    class Media:
        css = {
        'all': ('admin/css/custom_project.css',)  # Custom CSS (if needed)
        }
        js = ('admin/js/custom_project.js',)  # Custom JS for additional interactivity
    
# Team Admin
@admin.register(Team, site=admin_site)
class TeamAdmin(HiddenAdmin):
    list_display = ('team_name',) # , 'created_by'
    search_fields = ('team_name',)
    # filter_horizontal = ('members',)

# TeamMember Admin
@admin.register(TeamMember, site=admin_site)
class TeamMemberAdmin(HiddenAdmin):
    list_display = ('team', 'user', 'joined_at')
    list_filter = ('joined_at',)
    search_fields = ('team__team_name', 'user__username')  # Update `username` with the field used in `Employee`

# Comment Admin
@admin.register(Comment, site=admin_site)
class CommentAdmin(HiddenAdmin):
    list_display = ('task', 'content', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'task__task_name')

# ProjectTeam Admin
@admin.register(ProjectTeam, site=admin_site)
class ProjectTeamAdmin(HiddenAdmin):
    list_display = ('project', 'team')
    search_fields = ('project__project_name', 'team__team_name')

# Clients Admin
@admin.register(Clients, site=admin_site)
class ClientsAdmin(admin.ModelAdmin):
    list_display = ('Client_Number', 'Client_Name', 'Client_Country', 'Client_City', 'Client_ID')
    search_fields = ('Client_Name', 'Client_Country__country_name', 'Client_City__city_name')  # Use double underscores for related fields
    readonly_fields = ('Client_ID',)
    # class Meta:
    #     model = Clients
    #     fields = '__all__'

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)

    #     # Determine filtering for employee_type based on the request data or existing instance
    #     if 'country' in self.fields:
    #         try:
    #             country_id = int(self.data.get('country'))
    #             # self.fields['employee_type'].queryset = EmployeeType.objects.filter(country_id=country_id)
    #             # self.fields['state'].queryset = State.objects.filter(country_id=country_id)
    #             self.fields['city'].queryset = City.objects.filter(country_id=country_id)

    #         except (ValueError, TypeError):
    #             # self.fields['employee_type'].queryset = EmployeeType.objects.none()
    #             # self.fields['state'].queryset         = State.objects.none()
    #             self.fields['city'].queryset          = City.objects.none()

    #     elif self.instance and self.instance.pk:
    #         #  self.fields['employee_type'].queryset = EmployeeType.objects.filter(country=self.instance.country)
    #         #  self.fields['state'].queryset =  State.objects.filter(country=self.instance.country)
    #          self.fields['city'].queryset =  City.objects.filter(country=self.instance.country)

    #     else:
    #         # self.fields['employee_type'].queryset = EmployeeType.objects.none()
    #         # self.fields['state'].queryset = State.objects.none()
    #         self.fields['city'].queryset = City.objects.none()
    #     # self.fields['continent'].widget.attrs.update({
    #     # 'id': 'idd_continent'
    #     # })
    #     # Set up dynamic masking for fields     

# Project Admin

# Location and Department Admins

class CountryForm(forms.ModelForm):
    class Meta:
        model = Country
        fields = '__all__'
    # def clean_continent(self):
    #     continent = self.cleaned_data.get('continent')
    #     if not continent:
    #         raise forms.ValidationError("A valid continent must be selected.")
    #     return continent
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set custom empty_label for the continent field
        if 'Continent' in self.fields:
            self.fields['Continent'].empty_label = "Select Continent"

@admin.register(Country, site=admin_site)
class CountryAdmin(BaseLocationAdmin):
    form = CountryForm
    list_display = ('country_name', 'country_code', 'continent')#, 'region'
    def save(self, *args, **kwargs):
        # if not Continent.objects.filter(pk=self.continent_id).exists():
        #     raise ValueError(f"Selected continent (ID: {self.continent_id}) does not exist.")
        super().save(*args, **kwargs)
    def save_model(self, request, obj, form, change):
        # if not Continent.objects.filter(pk=obj.continent_id).exists():
        #     raise ValueError(f"Selected continent (ID: {obj.continent_id}) does not exist.")
        super().save_model(request, obj, form, change)

# class CityForm(forms.ModelForm):
#     class Meta:
#         model = City
#         fields = '__all__'

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # Set custom empty_label for country_id
#         if 'country_id' in self.fields:
#             self.fields['country_id'].empty_label = "Select Country"

class CityForm(forms.ModelForm):
    class Meta:
        model = City
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set custom empty_label for state_id
        if 'state_id' in self.fields:
            self.fields['state_id'].empty_label = "Select State"
        # Set custom empty_label for country_id
        if 'country_id' in self.fields:
            self.fields['country_id'].empty_label = "Select Country"

@admin.register(City, site=admin_site)
class CityAdmin(BaseLocationAdmin):
    form = CityForm
    list_display = ('city_name', 'postal_code', 'state_id', 'country_id')

@admin.register(State, site=admin_site)
class StateAdmin(BaseLocationAdmin):
    Form = CityForm
    list_display = ('state_name', 'state_code', 'country_id')

class ContinentForm(forms.ModelForm):
    class Meta:
        model = Continent
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set custom empty_label for fields (e.g., dropdown placeholder)
        self.fields['continent_name'].empty_label = "Select Continent"  # Replace with custom text

@admin.register(Continent, site=admin_site)
class ContinentAdmin(BaseLocationAdmin):
    form = ContinentForm
    list_display = ('continent_name', 'continent_code')

@admin.register(Department, site=admin_site)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('department_name', 'location')
    search_fields = ('department_name',)

@admin.register(Designation, site=admin_site)
class DesignationAdmin(admin.ModelAdmin):
    list_display = ('designation_name',)
    search_fields = ('designation_name',)

# Custom GroupAdmin
class CustomGroupAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    filter_horizontal = ('permissions',)

admin_site.register(Group, CustomGroupAdmin)

