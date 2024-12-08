from django.db import models

class Continent(models.Model):
    continent_id = models.BigAutoField(primary_key=True)
    continent_name = models.CharField(max_length=100)
    continent_code = models.CharField(max_length=2, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def _str_(self):
        return self.continent_name


class Country(models.Model):
    country_id = models.AutoField(primary_key=True)
    continent_id = models.ForeignKey('Continent', on_delete=models.SET_NULL, null=True, related_name='country_continent_fk')
    country_name = models.CharField(max_length=100)
    country_code = models.CharField(max_length=3, unique=True)
    region = models.CharField(max_length=100, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def _str_(self):
        return self.country_name


class State(models.Model):
    state_id = models.AutoField(primary_key=True)
    country_id = models.ForeignKey('Country', on_delete=models.SET_NULL, null=True, related_name='state_country_fk')
    state_name = models.CharField(max_length=100)
    state_code = models.CharField(max_length=10, null=True, blank=True)    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def _str_(self):
        return self.state_name


class City(models.Model):
    city_id = models.AutoField(primary_key=True)
    country_id = models.ForeignKey('Country', on_delete=models.SET_NULL, null=True, related_name='city_country_fk')
    state_id = models.ForeignKey('State', on_delete=models.SET_NULL, null=True, related_name='city_state_fk')
    city_name = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def _str_(self):
        return self.city_name


class Designation(models.Model):
    designation_id = models.AutoField(primary_key=True)
    designation_name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def _str_(self):
        return self.designation_name


class Department(models.Model):
    department_id = models.AutoField(primary_key=True)
    department_name = models.CharField(max_length=100)
    location = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def _str_(self):
        return self.department_name


class Employee(models.Model):
    employee_id = models.BigAutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    nic_number = models.CharField(max_length=20, null=True, blank=True)
    Passport_number = models.CharField(max_length=15, null=True, blank=True)
    hire_date = models.DateField()
    left_date = models.DateField(null=True)
    job_title = models.CharField(max_length=50)
    department_id = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='employee_department_fk')
    designation_id = models.ForeignKey(Designation, on_delete=models.SET_NULL, null=True)
    country_id = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)
    state_id = models.ForeignKey(State, on_delete=models.SET_NULL, null=True)
    city_id = models.ForeignKey(City, on_delete=models.SET_NULL, null=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def _str_(self):
        return f"{self.first_name} {self.last_name}"