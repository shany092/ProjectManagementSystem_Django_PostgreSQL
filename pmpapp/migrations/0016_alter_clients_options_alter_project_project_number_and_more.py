# Generated by Django 5.1.2 on 2025-01-07 16:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pmpapp', '0015_project_team_members'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='clients',
            options={'verbose_name_plural': 'Clients'},
        ),
        migrations.AlterField(
            model_name='project',
            name='Project_number',
            field=models.BigIntegerField(unique=True),
        ),
        migrations.AlterField(
            model_name='projecttype',
            name='abbreviation',
            field=models.CharField(max_length=1),
        ),
    ]
