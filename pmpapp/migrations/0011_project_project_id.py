# Generated by Django 5.1.2 on 2025-01-05 20:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pmpapp', '0010_project_client_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='project_id',
            field=models.CharField(default=1, editable=False, max_length=150),
            preserve_default=False,
        ),
    ]
