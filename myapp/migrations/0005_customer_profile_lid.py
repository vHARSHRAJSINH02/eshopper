# Generated by Django 5.0.2 on 2024-02-27 12:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0004_rename_area_customer_profile_area_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer_profile',
            name='lid',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.signupuser'),
        ),
    ]
