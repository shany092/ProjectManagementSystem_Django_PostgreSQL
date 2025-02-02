# Generated by Django 5.1.2 on 2025-01-07 19:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pmpapp', '0016_alter_clients_options_alter_project_project_number_and_more'),
    ]

    operations = [
        
        migrations.AddField(
    model_name='project',
    name='project_name',
    field=models.CharField(max_length=100),
),
        migrations.RenameField(
            model_name='project',
            old_name='Client_Name',
            new_name='Client_ID',
        ),
        migrations.AlterField(
        model_name='project',
        name='Client_ID',
        field=models.ForeignKey(
            to='pmpapp.Clients',
            db_column="Client_ID",
            on_delete=models.CASCADE,
            to_field="Client_Number",
    ),
        ),
    ]
