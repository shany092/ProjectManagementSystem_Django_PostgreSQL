# Generated by Django 5.1.2 on 2025-01-14 07:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pmpapp', '0029_alter_employee_user_alter_project_team_members_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='employeeprofile',
            old_name='user',
            new_name='employee_profile',
        ),
    ]
