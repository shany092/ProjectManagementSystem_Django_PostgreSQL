# Generated by Django 5.1.2 on 2025-01-11 15:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pmpapp', '0024_remove_project_project_interval_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='task',
            unique_together=set(),
        ),
        migrations.AlterField(
            model_name='task',
            name='parent_task',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subtasks', to='pmpapp.task'),
        ),
    ]
