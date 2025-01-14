# Generated by Django 5.1.2 on 2025-01-05 22:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pmpapp', '0014_remove_project_team_members_task_team_members'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='team_members',
            field=models.ManyToManyField(blank=True, related_name='projects', to='pmpapp.employee'),
        ),
    ]
