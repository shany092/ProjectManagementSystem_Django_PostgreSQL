from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from .models import Task, Employee

class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="Email", max_length=254)

    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if email and password:
            self.user_cache = authenticate(self.request, email=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError("Invalid email or password.")
        return self.cleaned_data

class SubTaskForm(forms.ModelForm):
    task = forms.ModelChoiceField(queryset=Task.objects.all(), label="Parent Task",
            help_text="Select a task assigned to you.")

    class Meta:
        model = Task
        fields = ['task_name', 'due_date', 'priority', 'status', 'team_members', 'task']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['team_members'].queryset = Employee.objects.all()

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['task_name', 'due_date', 'status', 'priority']  # Fields relevant to sub-task

