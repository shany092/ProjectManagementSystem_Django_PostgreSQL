# Generated by Django 5.1.2 on 2025-01-17 19:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pmpapp', '0032_remove_customuser_employee_profile_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='sr_no',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
