from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.urls import reverse
from django.templatetags.static import static
from django.utils.safestring import mark_safe
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.utils.functional import cached_property
from django.contrib.auth.models import Group, Permission
from django.contrib.admin import AdminSite
from django.urls import path
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from pmpapp.models import EmployeeType, EmployeeCodeRule, Employee, Project, Department, Designation, CustomUser, City, Continent, Country, State

# Custom AdminSite
class MyCustomAdminSite(AdminSite):
    # use site_header along with admin.site to change the left top title text
    admin.site.site_header = "Mekex | Innovation"
    admin.site.site_title = "MKX"
    admin.site.index_title = "Mekex Innovation"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.dashboard_view)),
        ]
        return custom_urls + urls

    def dashboard_view(self, request):
        return render(request, "index.html")
    def has_permission(self, request):
        # Allow active users to access admin, regardless of 'is_staff'
        user = request.user
        return user.is_active  # Customize as needed, e.g., based on specific permissions


admin_site = MyCustomAdminSite(name="mypmpadmin")

# Custom UserAdmin
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    # readonly_fields = ('date_joined',)
    readonly_fields = ('username', 'is_active', 'is_staff', 'date_joined', 'email', 'first_name', 'last_name')# 'email',
    
     # Disable "Add" button
    def has_add_permission(self, request):
        return False
    # Disable editing by restricting change permission
    def has_change_permission(self, request, obj=None):
        """
        Allow changes only to the permissions tab.
        """
        if obj:
            return True  # Let editing happen if 'permissions' is selected
        return True  # Allow listing users

    # Prevent deleting users
    def has_delete_permission(self, request, obj=None):
        return False

    # Limit the permissions display in the form
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        if 'user_permissions' in form.base_fields:
            form.base_fields.pop('user_permissions')  # Remove the field
            for field_name in form.base_fields:
                if field_name != "groups":  # Make everything readonly except 'groups'
                    form.base_fields[field_name].disabled = True
        return form
    def save_model(self, request, obj, form, change):
        # Restrict saving only to group assignment
        if 'groups' not in form.changed_data:
            raise forms.ValidationError("You can only modify the 'groups' field.")
        super().save_model(request, obj, form, change)

    # Customize fieldsets for Permissions tab
    fieldsets = (
        (None, {'fields': ('username', 'email')}),
        ('Groups & Permissions', {'fields': ('groups',)}),
    )

        
        # # If editing an existing user, filter permissions
        # if obj:
        #     group_permissions = Permission.objects.filter(group__user=obj).distinct()
        #     form.base_fields['user_permissions'].queryset = group_permissions
        # else:
        #     # When creating a user, there are no group-specific permissions yet
        #     form.base_fields['user_permissions'].queryset = Permission.objects.none()
        
       
    
    # Customize the fieldsets if necessary
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups')}),# , 'user_permissions' include if user permissions are required
        ('Important Dates', {'fields': ('date_joined',)}),
    )

admin_site.register(CustomUser, CustomUserAdmin)

# Employee Admin
class EmployeeAdminForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = '__all__'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'country' in self.data:
            country_id = self.data.get('country')
            self.fields['employee_type'].queryset = EmployeeType.objects.filter(country_id=country_id)
        elif self.instance.pk:
            self.fields['employee_type'].queryset = EmployeeType.objects.filter(country=self.instance.country)
        # if self.instance and self.instance.country:
        #     self.fields['employee_type'].queryset = EmployeeType.objects.filter(
        #         country=self.instance.country
        #     )
        # self.fields['country'].queryset = Country.objects.all()
        self.fields['phone_number'].widget.attrs.update({
            'class': 'phone-input',  # Add a class for JavaScript targeting
            'data-mask': ''  # Placeholder for dynamic masking
        })
        self.fields['nic_number'].widget.attrs.update({
            'class': 'nic_number-input',  # Add a class for JavaScript targeting
            'data-mask': ''  # Placeholder for dynamic masking
        })

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
    # class Media:
    #    js = (
    #         # "admin/js/jquery.min.js",
    #         'admin/js/jquery.mask.js',
    #         # "admin/js/mask.min.js",
    #         "admin/js/employee_dynamic_filtering.js"
    #        )

    form = EmployeeAdminForm
    list_display = ( 'employee_code', 'first_name', 'last_name', 'email', 'employee_type', 'is_active')
    search_fields = ('first_name', 'last_name', 'email', 'employee_code')
    list_filter = ('employee_type', 'is_active', 'created_at')
    readonly_fields = ('employee_code',)  # Ensure employee_code is auto-generated
    exclude = ('user',)  # Remove the user field from the form

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
                'continent',
                
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
    list_display = ('code_prefix', 'starting_number') #, 'get_employee_type_name')
    form = EmployeeCodeRuleForm
    # To display the employee type name in listing
    # def get_employee_type_name(self, obj):
    #     return obj.employee_type.name if obj.employee_type else "-"
    # get_employee_type_name.short_description = 'Employee Type'

# Project Admin
@admin.register(Project, site=admin_site)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('project_name', 'start_date', 'end_date')
    search_fields = ('project_name',)
    list_filter = ('start_date', 'end_date')

# Location and Department Admins

class CountryForm(forms.ModelForm):
    class Meta:
        model = Country
        fields = '__all__'
    def clean_continent(self):
        continent = self.cleaned_data.get('continent')
        if not continent:
            raise forms.ValidationError("A valid continent must be selected.")
        return continent
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set custom empty_label for the continent field
        self.fields['continent'].empty_label = "Select Continent"

@admin.register(Country, site=admin_site)
class CountryAdmin(BaseLocationAdmin):
    form = CountryForm
    list_display = ('country_name', 'country_code', 'continent')#, 'region'
    def save(self, *args, **kwargs):
        if not Continent.objects.filter(pk=self.continent_id).exists():
            raise ValueError(f"Selected continent (ID: {self.continent_id}) does not exist.")
        super().save(*args, **kwargs)
    def save_model(self, request, obj, form, change):
        if not Continent.objects.filter(pk=obj.continent_id).exists():
            raise ValueError(f"Selected continent (ID: {obj.continent_id}) does not exist.")
        super().save_model(request, obj, form, change)

class CityForm(forms.ModelForm):
    class Meta:
        model = City
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set custom empty_label for country_id
        if 'country_id' in self.fields:
            self.fields['country_id'].empty_label = "Select Country"

@admin.register(State, site=admin_site)
class StateAdmin(BaseLocationAdmin):
    Form = CityForm
    list_display = ('state_name', 'state_code', 'country_id')

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
