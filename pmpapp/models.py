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
from django.db.models import Max
from django.core.exceptions import ValidationError

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
        extra_fields.setdefault('is_staff', True)

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

    class Meta:
        verbose_name = "Authentication and Authorization"
        verbose_name_plural = "Users"
    

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
    country = models.ForeignKey('country', on_delete=models.CASCADE, related_name='employee_Types', null=True )
    class Meta:
        verbose_name = "Employee Type"
        verbose_name_plural = "Employee Types"

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
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    nic_number = models.CharField(max_length=20, null=True, blank=True, unique=True)
    passport_number = models.CharField(max_length=15, null=True, blank=True, unique=True)
    date_joined = models.DateField()
    left_date = models.DateField(null=True, blank=True)
    job_title = models.CharField(max_length=50)
    department = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True)
    designation = models.ForeignKey('Designation', on_delete=models.SET_NULL, null=True)
    # continent = models.ForeignKey('Continent', on_delete=models.SET_NULL, null=True, blank=True)
    country = models.ForeignKey('Country', on_delete=models.CASCADE, related_name="employee_types")
    state = models.ForeignKey('State', on_delete=models.SET_NULL, null=True, related_name='employees')
    city = models.ForeignKey('City', on_delete=models.SET_NULL, null=True, related_name='employees')
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    class Meta:
        verbose_name = "Employee"
        verbose_name_plural = "Employees"

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

class ProjectType(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Full name of the project type
    description = models.TextField(blank=True, null=True)  # Optional detailed description
    abbreviation = models.CharField(max_length=1)  # Two-letter code (e.g., 'CO', 'OT')

    class Meta:
        verbose_name = "Project Type"
        verbose_name_plural = "Project Types"

    def __str__(self):
        return f"{self.name} ({self.abbreviation})"
        
class ProjectInterval(models.Model):
    name = models.CharField(max_length=255, unique=True)  # Name of the interval (e.g., "Weekly", "Sprint")
    interval = models.PositiveIntegerField(unique=True)  # Numerical identifier (e.g., 0, 1, 2, etc.)

    class Meta:
        verbose_name = "Project Interval"
        verbose_name_plural = "Project Intervals"

    def __str__(self):
        return f"{self.name} ({self.interval})"
       
class Project(models.Model):
    """Model representing a project."""
    STATUS_CHOICES = [
        ('Not Started', 'Not Started'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]
    Client_ID = models.ForeignKey('Clients', on_delete=models.SET_NULL, null=True ,db_column="Client_ID", to_field='Client_ID')
    project_type = models.ForeignKey(ProjectType, on_delete=models.SET_NULL, null=True, related_name="projects")
    # project_interval = models.ForeignKey(ProjectInterval, on_delete=models.SET_NULL, null=True, related_name="projects")
    id = models.BigAutoField(primary_key=True)
    Project_number = models.BigIntegerField(unique=True)
    project_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Not Started')
    created_by = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True, related_name="created_projects")
    project_id = models.CharField(max_length=150, editable=False, unique=True)  # Ensure uniqueness
    team_members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="projects", blank=True)  # Team Members
    
    def get_next_project_number(self):
        # Query to get the current highest Project_number
        last_project = Project.objects.aggregate(Max('Project_number'))
        if last_project['Project_number__max']:
            next_number = last_project['Project_number__max'] + 1
        else:
            next_number = 600  # Start the sequence at 600 if there are no projects
        return next_number
    
    def save(self, *args, **kwargs):
        # Generate `project_id` dynamically before saving
        if not self.Project_number:
            self.Project_number = self.get_next_project_number()
        if not self.pk:  # Ensure this block runs only on object creation
            type_code = self.project_type.abbreviation if self.project_type else "XX"  # Default abbreviation if null
            # interval_code = str(self.project_interval.interval) if self.project_interval else "00"  # Default count if null
            self.project_id = f"{self.Project_number}-{type_code}" #-{interval_code}

        super().save(*args, **kwargs)  # Call the parent's save method

    def __str__(self):
        return self.project_name if self.project_name else "Unnamed Project"

class Task(models.Model):
    """Model representing a task within a project."""
    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]
    STATUS_CHOICES = [
        ('Not Started', 'Not Started'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]
    project = models.ForeignKey('Project', on_delete=models.CASCADE,null=False)
   # project_id = models.ForeignKey('Project', on_delete=models.CASCADE, null=False)
    task_name = models.CharField(max_length=100)
    sr_no = models.CharField(max_length=255, blank=True, null=True, unique=True)  # Will store SR. No
    due_date = models.DateField(blank=True, null=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='Medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Not Started')
    team_members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="tasks", blank=True)  # Team members assigned to the task
    parent_task = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subtasks') #  limit_choices_to=models.Q(parent_task__isnull=True)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='assigned_tasks')

    class Meta:
        permissions = [
            ('can_add_subtasks', 'Can add sub-tasks'),
        ]
    # def clean(self):
    #     """Ensure the sub task and parent task belongs to the same project."""
    #     if self.parent_task and self.parent_task.project != self.project:
    #         raise ValidationError("The parent task must belong to the same project.")
    # class Meta:
    #     unique_together = ('project', 'parent_task')  # Enforce the project and parent_task combination uniqueness
   
    def save(self, *args, **kwargs):
        try:
            # Check if the task is new (does not exist in the database yet)
            is_new = self.pk is None

            # Handle sub-task scenario
            if self.parent_task_id:
                # Fetch the parent task
                parent_task = Task.objects.get(pk=self.parent_task_id)

                # Ensure the current task inherits the project from the parent task
                if not self.project_id and parent_task.project_id:
                    self.project_id = parent_task.project_id

                # Derive Sr. No. for sub-task only if the task is new or parent_task_id is being changed
                if is_new or not self.sr_no or self.parent_task_id != self.__class__.objects.get(pk=self.pk).parent_task_id:
                    sibling_count = Task.objects.filter(parent_task_id=self.parent_task_id).count() + 1
                    self.sr_no = f"{parent_task.sr_no}.{sibling_count}"

            # Handle top-level task scenario
            elif self.project_id:
                # Derive Sr. No. for top-level tasks in the project
                if is_new or not self.sr_no:
                    main_task_count = Task.objects.filter(project_id=self.project_id, parent_task_id__isnull=True).count() + 1
                    self.sr_no = f"{self.project_id}.{main_task_count}"

            # Raise an error if the task does not belong to a project or parent task
            else:
                raise ValueError("Task must be associated with either a project or a parent task.")

            # Save the task
            super().save(*args, **kwargs)

        except Exception as e:
            # Print debug info if an error occurs
            print(f"Error saving task: {self}. Exception: {e}")
            raise

        # Perform any post-save logic
        try:
            if self.parent_task_id:
                # Fetch the parent task again after save (if necessary)
                parent_task = Task.objects.get(pk=self.parent_task_id)
                # Ensure project is updated properly if not already set
                if not self.project_id and parent_task.project_id:
                    self.project_id = parent_task.project_id

            elif self.project_id:
                # No additional logic required for top-level tasks (optional placeholder)
                pass

        except Task.DoesNotExist:
            print(f"Parent task with ID {self.parent_task_id} does not exist.")

        
    # def save(self, *args, **kwargs):
    #     # Ensure project is set if the task has a parent task
    #     if not self.project and self.parent_task_id:
    #         # Manually fetch the parent task and its project
    #         parent_task = Task.objects.get(pk=self.parent_task_id)
    #         self.project = parent_task.project

    #     print(self)
    #     # Call the original save method
    #     super().save(*args, **kwargs)
    
    # def save(self, *args, **kwargs):
    #     try:
    #         # Case 1: Handle sub-tasks
    #         if self.parent_task_id:
    #             # Fetch the parent task
    #             parent_task = Task.objects.get(pk=self.parent_task_id)
    #             # Ensure the current task inherits the project from the parent task
    #             if not self.project_id and parent_task.project_id:
    #                 self.project_id = parent_task.project_id

    #             # Derive Sr. No. for sub-task
    #             sibling_count = Task.objects.filter(parent_task_id=self.parent_task_id).count() + 1
    #             self.sr_no = f"{parent_task.sr_no}.{sibling_count}"

    #         # Case 2: Handle top-level tasks
    #         elif self.project_id:
    #             # Derive Sr. No. for top-level tasks in the project
    #             main_task_count = Task.objects.filter(project_id=self.project_id, parent_task_id__isnull=True).count() + 1
    #             self.sr_no = f"{self.project.id}.{main_task_count}"

    #         # Case 3: Edge case where no project or parent task exists
    #         else:
    #             raise ValueError("Task must be associated with either a project or a parent task.")

    #         # Save the task
    #         super().save(*args, **kwargs)

    #     except Exception as e:
    #         # Print debug info if there's an exception
    #         print(f"Error occurred while saving task: {self}. Exception: {e}")
    #         raise

    #     # Additional validation/logic after saving if needed
    #     if self.parent_task_id:
    #         try:
    #             # Fetch and update parent-related fields post-save
    #             parent_task = Task.objects.get(pk=self.parent_task_id)
    #             if not self.project_id and parent_task.project_id:
    #                 self.project_id = parent_task.project_id

    #         except Task.DoesNotExist:
    #             print(f"Parent task with ID {self.parent_task_id} does not exist.")

    #     elif self.project_id:
    #         # Logic for top-level tasks if required post-save
    #         pass

    # def save2(self, *args, **kwargs):
    #     try:
    #         # Case 1: Handle if task has a parent (sub-task scenario)
    #         if self.parent_task_id:
    #             print(f"1st case: {self}")
    #             # Fetch the parent task
    #             parent_task = Task.objects.get(pk=self.parent_task_id)
    #             print(f"parent task: {parent_task}")
                
    #             # Derive Sr. No. for the current task based on parent's Sr. No.
    #             sibling_count = Task.objects.filter(parent_task_id=self.parent_task_id).count() + 1
    #             self.sr_no = f"{parent_task.sr_no}.{sibling_count}"
    #             print(f"parent task: on line 298 {self.sr_no}")

    #             # Inherit the project from the parent task if not set
    #             if not self.project_id and parent_task.project_id:
    #                 self.project_id = parent_task.project_id
    #                 print(f"parent task: on line 303 {self.project_id}")

    #         # Case 2: Handle top-level tasks (no parent task)
    #         elif self.project_id:
    #             # Calculate based on the project's existing tasks
    #             main_task_count = Task.objects.filter(project_id=self.project_id, parent_task_id__isnull=True).count() + 1
    #             self.sr_no = f"{self.project.id}.{main_task_count}"
    #             print(f"2nd case: {self.sr_no}")

    #         # Case 3: Edge case for tasks with no project or parent (Optional)
    #         else:
    #             print("Error: Task must belong to either a project or a parent task.")
    #             raise ValueError("Task must be associated with a project or a parent task.")

    #         # Save the object
    #         super().save(*args, **kwargs)

    #     except Exception as e:
    #         # Handle any exceptions and print debug info
    #         print(f"Error saving task: {self}. Exception: {e}")
    #         raise
        
    #     try:
    #         if not self.parent_task_id:
    #             # Try manually fetching the parent task
    #             parent_task = Task.objects.get(pk=self.parent_task_id)
    #             # print(f"Fetched parent task: {parent_task}, Project: {parent_task.project}")
    #             if not self.project_id and parent_task.project_id:
    #                 self.project_id = parent_task.project_id
    #                 self.sr_no = Project.id
    #             else:
    #                 print("Project already set or parent task has no project.")
    #         else:
    #             print("No parent task provided.")
    #         # Automatically set the Sr. No on saving task       
    #         # Call the original save method
    #         # Calculate Sr. No
    #         if self.parent_task_id:
    #             if not self.sr_no:
    #             # If it's a sub-task, derive Sr. No from parent task
    #               self.sr_no = f"{self.parent_task_id.sr_no}.{self._meta.model.objects.filter(parent_task_id=self.parent_task_id).count() + 1}"
                
    #         elif self.project:
    #             # If it's a main task, it gets a project-based Sr. No
    #             self.sr_no = f"{self.project.id}.{self._meta.model.objects.filter(project=self.project).count() + 1}"

    #         super().save(*args, **kwargs)
    #     except Exception as e:
    #         print(f"Saving task: {self}")
    #         print(f"Parent task ID: {self.parent_task_id}")
    #         print(f"Assigned project from parent task: {self.project}")
    #         print(f"Error occurred while saving task: {e}")
    #     # raise  # Optional: Re-raise the exception
    
    # def save2(self, *args, **kwargs):
    #     # Derive sr_no before saving
    
    #     if not self.sr_no:
    #         if self.parent_task:
    #             # Subtask scenario
    #             parent_task = Task.objects.get(pk=self.parent_task_id)
    #             self.project_id = parent_task.project_id
    #             sibling_count = self.parent_task.subtasks.count() + 1
    #             self.sr_no = f"{self.parent_task.sr_no}.{sibling_count}"
                
                
    #     else:
    #         # Top-level task scenario
    #         main_task_count = (Task.objects.filter(project=self.project, parent_task__isnull=True).count() + 1)
    #         self.sr_no = f"{self.project.id}.{main_task_count}"
    #     super().save(*args, **kwargs)
    
    # def save(self, *args, **kwargs):
    #     try:
    #         # Handle sub-task scenario
    #         if self.parent_task_id:
    #             # Fetch the parent task
    #             parent_task = Task.objects.get(pk=self.parent_task_id)

    #             # Ensure the current task inherits the project from the parent task
    #             if not self.project_id and parent_task.project_id:
    #                 self.project_id = parent_task.project_id

    #             # Derive Sr. No. for sub-task
    #             sibling_count = Task.objects.filter(parent_task_id=self.parent_task_id).count() + 1
    #             self.sr_no = f"{parent_task.sr_no}.{sibling_count}"

    #         # Handle top-level task scenario
    #         elif self.project_id:
    #             # Derive Sr. No. for top-level tasks in the project
    #             main_task_count = Task.objects.filter(project_id=self.project_id, parent_task_id__isnull=True).count() + 1
    #             self.sr_no = f"{self.project_id}.{main_task_count}"

    #         # Raise an error if the task does not belong to a project or parent task
    #         else:
    #             raise ValueError("Task must be associated with either a project or a parent task.")

    #         # Save the task
    #         super().save(*args, **kwargs)

    #     except Exception as e:
    #         # Print debug info if an error occurs
    #         print(f"Error saving task: {self}. Exception: {e}")
    #         raise

    #     # Perform any post-save logic
    #     try:
    #         if self.parent_task_id:
    #             # Fetch the parent task again after save (if necessary)
    #             parent_task = Task.objects.get(pk=self.parent_task_id)
    #             # Ensure project is updated properly if not already set
    #             if not self.project_id and parent_task.project_id:
    #                 self.project_id = parent_task.project_id

    #         elif self.project_id:
    #             # No additional logic required for top-level tasks (optional placeholder)
    #             pass

    #     except Task.DoesNotExist:
    #         print(f"Parent task with ID {self.parent_task_id} does not exist.")

    # def get_next_task_number(self):
    #     # This is a helper to find the next task number for child tasks
    #     sibling_tasks = self.parent_task.sub_tasks.all()
    #     return len(sibling_tasks) + 1
    
    def __str__(self):
        return f"{self.task_name} ({self.sr_no})"

class Clients(models.Model):
    Client_Number = models.AutoField(primary_key=True)  
    Client_Name = models.CharField(max_length=150)
    Client_Country = models.ForeignKey('Country', on_delete=models.SET_NULL, null=True)
    Client_City = models.ForeignKey('City', on_delete=models.SET_NULL, null=True)
    Client_ID = models.CharField(max_length=150, editable=False, unique=True)  # Make it non-editable in the admin UI

    def save(self, *args, **kwargs):
        # Generate Client_ID dynamically
        if not self.pk:
            super().save(*args, **kwargs)  # Save first to get Client_Number
        country_code = self.Client_Country.country_name[:2].upper() if self.Client_Country else "NC"
        city_code = self.Client_City.city_name[:2].upper() if self.Client_City else "NA"
        self.Client_ID = f"{self.Client_Number}-{self.Client_Name[:4].upper()}-{country_code}{city_code}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.Client_ID
    class Meta:
        verbose_name_plural = "Clients"  # Set plural name here

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
    continent = models.ForeignKey('Continent', on_delete=models.CASCADE, null=True, related_name= 'countries')# related_name='country_continent_fk')
    country_name = models.CharField(max_length=100)
    country_code = models.CharField(max_length=3, unique=True)
    # region = models.CharField(max_length=100, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    phone_number_mask = models.CharField(max_length=20, blank=True, null=True)  # Mask pattern
    cnic_number_mask = models.CharField(max_length=20, blank=True, null=True)  # Mask pattern

    class Meta:
        verbose_name_plural = "Countries"  # Set plural name here

    def __str__(self):
        return self.country_name

class State(models.Model):
    state_id = models.AutoField(primary_key=True)
    country = models.ForeignKey('Country',on_delete=models.SET_NULL, null=True, related_name='state') #related_name='state_country_fk')
    state_name = models.CharField(max_length=100)
    state_code = models.CharField(max_length=10, null=True, blank=True)    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.state_name

class City(models.Model):
    city_id = models.AutoField(primary_key=True)
    country = models.ForeignKey('Country', on_delete=models.SET_NULL, null=True,related_name='city') #related_name='city_country_fk')
    state = models.ForeignKey('State', on_delete=models.SET_NULL, null=True, related_name='city_state_fk')
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

class Team(models.Model):
    """Model representing a team."""
    team_name = models.CharField(max_length=100)

    created_by = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True, related_name="created_teams")
    members = models.ManyToManyField('Employee', through="TeamMember", related_name="teams")

    def __str__(self):
        return self.team_name

class TeamMember(models.Model):
    """Model for associating users with teams."""
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    user = models.ForeignKey('Employee', on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name()} in {self.team.team_name}"

class Comment(models.Model):
    """Model representing comments on tasks."""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="comments")
    # user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.task.task_name}"

class ProjectTeam(models.Model):
    """Model for associating teams with projects."""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="project_teams")
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="team_projects")

    def __str__(self):
        return f"Team {self.team.team_name} on Project {self.project.project_name}"


    