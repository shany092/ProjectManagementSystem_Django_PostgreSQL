# import random
# import secrets
# import string
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db import models
from django.conf import settings  # To access AUTH_USER_MODEL
# from django.contrib.auth.models import UserManager
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone

# Manager for Custom User




# Custom Manager for User model
class CustomUserManager(BaseUserManager):
    def create_user(self, email, username=None, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        if username is None:
            username = f"default_{get_random_string(8)}"  # Generate a default username if not provided
            
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username=None, password=None, **extra_fields):
        """
        Create and return a superuser with email, username, and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        # Ensure critical fields are properly set
        if not extra_fields.get('is_staff'):
            raise ValueError('Superuser must have is_staff=True.')
        if not extra_fields.get('is_superuser'):
            raise ValueError('Superuser must have is_superuser=True.')
        
        # Generate a username if not provided
        if not username:
            username = f"superuser_{get_random_string(8)}"
        
        return self.create_user(email, username, password, **extra_fields)
# Custom User Model
class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']  # These fields will be prompted when creating a user via shell

    objects = CustomUserManager()
    
    def __str__(self):
        return self.email

    # Add permission methods
    def has_perm(self, perm, obj=None):
        """
        Return True if the user has the specified permission.
        For superusers, always return True.
        """
        return self.is_superuser

    def has_module_perms(self, app_label):
        """
        Return True if the user has permissions to view the app `app_label`.
        For superusers, always return True.
        """
        return self.is_superuser

class EmployeeType(models.Model):
    # employee_type_id = models.BigIntegerField(primary_key=True, null=False)
    name = models.CharField(max_length=50, unique=True)  # e.g., 'Italy Internal'
    description = models.TextField(null=True, blank=True)  # Optional field for detailed info

    def __str__(self):
        return self.name

class EmployeeCodeRule(models.Model):
    employee_type = models.OneToOneField(
        EmployeeType, 
        on_delete=models.CASCADE, 
        related_name='code_rule'
    )
    code_prefix = models.CharField(max_length=10)  # e.g., 'MKX1001'
    starting_number = models.IntegerField(default=1)  # e.g., Starting number

    def __str__(self):
        return f"{self.employee_type.name} - {self.code_prefix}"
    
CustomUser = get_user_model()

class Employee(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='employee_profile'
    )
    employee_type = models.ForeignKey(EmployeeType, on_delete=models.CASCADE)
    employee_code = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    nic_number = models.CharField(max_length=20, null=True, blank=True, unique=True)
    passport_number = models.CharField(max_length=15, null=True, blank=True, unique=True)
    date_joined = models.DateField()
    left_date = models.DateField(null=True, blank=True)
    job_title = models.CharField(max_length=50)
    department = models.ForeignKey('Department', on_delete=models.CASCADE, null=True)
    designation = models.ForeignKey('Designation', on_delete=models.SET_NULL, null=True)
    continent = models.ForeignKey('Continent', on_delete=models.SET_NULL, null=True, blank=True)
    country = models.ForeignKey('Country', on_delete=models.SET_NULL, null=True)
    state = models.ForeignKey('State', on_delete=models.SET_NULL, null=True)
    city = models.ForeignKey('City', on_delete=models.SET_NULL, null=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Generate the employee code if not already set
        if not self.employee_code:
            code_rule = EmployeeCodeRule.objects.filter(employee_type=self.employee_type).first()
            if not code_rule:
                raise ValueError(f"No code generation rule found for {self.employee_type.name}")

            prefix = code_rule.code_prefix
            last_code = Employee.objects.filter(employee_code__startswith=prefix).order_by('-employee_code').first()
            next_number = int(last_code.employee_code[len(prefix):]) + 1 if last_code else code_rule.starting_number
            self.employee_code = f"{prefix}{next_number:04d}"

        # Automatically create and associate CustomUser
        if not self.user_id:
            User = get_user_model()
            self.user = User.objects.create_user(
                email=self.email,
                username=self.employee_code,
                password='defaultpassword123',
                first_name=self.first_name,
                last_name=self.last_name,
                is_staff=self.is_staff,  # Copy these attributes if needed
                is_superuser=self.is_superuser
            )
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.employee_code})"


class Project(models.Model):
    """Model representing a project."""
    STATUS_CHOICES = [
        ('Not Started', 'Not Started'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]
    project_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Not Started')
    #created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_projects")

    def __str__(self):
        return self.project_name


#class (models.Model):
#     """Model representing a task within a project."""
#     PRIORITY_CHOICES = [
#         ('Low', 'Low'),
#         ('Medium', 'Medium'),
#         ('High', 'High'),
#     ]
#     STATUS_CHOICES = [
#         ('Not Started', 'Not Started'),
#         ('In Progress', 'In Progress'),
#         ('Completed', 'Completed'),
#     ]
#     project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
#     task_name = models.CharField(max_length=100)
#     #assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_tasks")
#     due_date = models.DateField(blank=True, null=True)
#     priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='Medium')
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Not Started')

#     def __str__(self):
#         return f"{self.task_name} - {self.project.project_name}"


# class Team(models.Model):
#     """Model representing a team."""
#     team_name = models.CharField(max_length=100)
#     # created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_teams")
#     # members = models.ManyToManyField(User, through="TeamMember", related_name="teams")

#     def __str__(self):
#         return self.team_name


# class TeamMember(models.Model):
#     """Model for associating users with teams."""
#     team = models.ForeignKey(Team, on_delete=models.CASCADE)
#     #user = models.ForeignKey(User, on_delete=models.CASCADE)
#     joined_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.user.get_full_name()} in {self.team.team_name}"


# class Comment(models.Model):
#     """Model representing comments on tasks."""
#     task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="comments")
#     # user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
#     content = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Comment by {self.user.username} on {self.task.task_name}"


# class ProjectTeam(models.Model):
#     """Model for associating teams with projects."""
#     project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="project_teams")
#     team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="team_projects")

#     def __str__(self):
#         return f"Team {self.team.team_name} on Project {self.project.project_name}"



class Continent(models.Model):
    continent_id = models.BigAutoField(primary_key=True)
    continent_name = models.CharField(max_length=100)
    continent_code = models.CharField(max_length=2, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.continent_name


class Country(models.Model):
    country_id = models.AutoField(primary_key=True)
    continent_id = models.ForeignKey('Continent', on_delete=models.SET_NULL, 
                                     null=True, related_name='country_continent_fk')
    country_name = models.CharField(max_length=100)
    country_code = models.CharField(max_length=3, unique=True)
    region = models.CharField(max_length=100, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name_plural = "Countries"  # Set plural name here

    def __str__(self):
        return self.country_name


class State(models.Model):
    state_id = models.AutoField(primary_key=True)
    country_id = models.ForeignKey('Country',
                                    on_delete=models.SET_NULL, null=True, related_name='state_country_fk')
    state_name = models.CharField(max_length=100)
    state_code = models.CharField(max_length=10, null=True, blank=True)    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.state_name


class City(models.Model):
    city_id = models.AutoField(primary_key=True)
    country_id = models.ForeignKey('Country',
                                    on_delete=models.SET_NULL, null=True, related_name='city_country_fk')
    state_id = models.ForeignKey('State', 
                                 on_delete=models.SET_NULL, null=True, related_name='city_state_fk')
    city_name = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name_plural = "Cities"  # Set plural name here

    def __str__(self):
        return self.city_name


class Designation(models.Model):
    designation_id = models.AutoField(primary_key=True)
    designation_name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.designation_name


class Department(models.Model):
    department_id = models.AutoField(primary_key=True)
    department_name = models.CharField(max_length=100)
    location = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.department_name
