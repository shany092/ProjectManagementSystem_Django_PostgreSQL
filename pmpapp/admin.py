from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django import forms
from django.contrib.auth.models import Group
from django.contrib.admin import AdminSite
from django.urls import path
from django.shortcuts import render
from django.contrib.auth import get_user_model
from pmpapp.models import EmployeeType, EmployeeCodeRule, Employee, Project, Department, Designation, CustomUser, City, Continent, Country, State

# Custom AdminSite
class MyCustomAdminSite(AdminSite):
    site_header = "MKX Mekex Innovation"
    site_title = "MKX"
    index_title = "Mekex Innovation"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.dashboard_view)),
        ]
        return custom_urls + urls

    def dashboard_view(self, request):
        return render(request, "index.html")

admin_site = MyCustomAdminSite(name="mypmpadmin")

# Custom UserAdmin
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    readonly_fields = ('date_joined',)

    # fieldsets = UserAdmin.fieldsets + (
    #     (None, {'fields': ('first_name',)}),
    # )
    # add_fieldsets = UserAdmin.add_fieldsets + (
    #     (None, {'fields': ('first_name',)}),
    # )

admin_site.register(get_user_model(), CustomUserAdmin)

# Employee Admin
class EmployeeAdminForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = '__all__'
        print(fields)

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
        # self.fields['employee_code'].widget.attrs['readonly'] = True
        # --------------------------------------------------------------------------------
        # This function can be used to select username at the top of the employee form    
    # def get_form(self, request, obj=None, **kwargs):
    #     form = super().get_form(request, obj, **kwargs)
    #     form.base_fields['user'].required = True  # Enforce selection of a user
    #     return form
        # ----------------------------------------------------------------------------------
@admin.register(Employee, site=admin_site)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'employee_code', 'employee_type', 'is_active')
    search_fields = ('first_name', 'last_name', 'email', 'employee_code')
    list_filter = ('employee_type', 'is_active', 'created_at')
    readonly_fields = ('employee_code',)  # Ensure employee_code is auto-generated
    exclude = ('user',)  # Remove the user field from the form

    fieldsets = (
        (None, {
            'fields': (
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
                'continent',
                'country',
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

@admin.register(EmployeeType, site=admin_site)
class EmpType(BaseLocationAdmin):
    list_display = ('name',)

@admin.register(EmployeeCodeRule, site=admin_site)
class EmpCodeRule(BaseLocationAdmin):
    list_display = ('code_prefix','starting_number')

# Project Admin
@admin.register(Project, site=admin_site)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('project_name', 'start_date', 'end_date')
    search_fields = ('project_name',)
    list_filter = ('start_date', 'end_date')

# Location and Department Admins

@admin.register(Country, site=admin_site)
class CountryAdmin(BaseLocationAdmin):
    list_display = ('country_name', 'country_code', 'region')

@admin.register(State, site=admin_site)
class StateAdmin(BaseLocationAdmin):
    list_display = ('state_name', 'state_code', 'country_id')

@admin.register(City, site=admin_site)
class CityAdmin(BaseLocationAdmin):
    list_display = ('city_name', 'postal_code', 'state_id', 'country_id')

@admin.register(Continent, site=admin_site)
class ContinentAdmin(BaseLocationAdmin):
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
