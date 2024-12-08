from django.contrib import admin
from .models import Continent,Country,State,City,Designation,Department,Employee
# Register your models here.


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'job_title', 'department_id', 'designation_id', 'status')
    search_fields = ('first_name', 'last_name', 'email', 'job_title')
    list_filter = ('status', 'department_id', 'designation_id')
    ordering = ('-created_at')

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('department_name', 'location')
    search_fields = ('department_name')

@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    list_display = ('designation_name')
    search_fields = ('designation_name')

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('country_name', 'country_code', 'region')
    search_fields = ('country_name', 'country_code')

@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ('state_name', 'state_code', 'country_id')
    search_fields = ('state_name')

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('city_name', 'postal_code', 'state_id', 'country_id')
    search_fields = ('city_name',)

@admin.register(Continent)
class ContinentAdmin(admin.ModelAdmin):
    list_display = ('continent_name', 'continent_code')
    search_fields = ('continent_name')

#admin.site.register(Continent, ContinentAdmin)
#admin.site.register(Country, CountryAdmin)
# admin.site.register(State, StateAdmin)
# admin.site.register(City, CityAdmin)
# admin.site.register(Designation, DesignationAdmin)
# admin.site.register(Department, DepartmentAdmin)
# admin.site.register(Employee, EmployeeAdmin)

