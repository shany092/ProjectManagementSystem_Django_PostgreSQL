# Generated by Django 5.1.2 on 2025-01-05 21:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pmpapp', '0012_alter_project_project_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='team_members',
            field=models.ManyToManyField(blank=True, related_name='projects', to='pmpapp.employee'),
        ),
    ]
