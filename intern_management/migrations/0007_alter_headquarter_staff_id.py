# Generated by Django 4.2.3 on 2023-07-22 14:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('intern_management', '0006_alter_headquarter_staff_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='headquarter',
            name='staff_id',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='intern_management.staffs'),
        ),
    ]
