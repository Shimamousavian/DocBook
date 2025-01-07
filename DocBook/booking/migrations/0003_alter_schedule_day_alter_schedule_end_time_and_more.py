# Generated by Django 5.1.4 on 2025-01-05 17:32

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0002_alter_doctor_schedule'),
    ]

    operations = [
        migrations.AlterField(
            model_name='schedule',
            name='day',
            field=models.CharField(choices=[('Saturday', 'Saturday'), ('Sunday', 'Sunday'), ('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday')], max_length=50),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='end_time',
            field=models.TimeField(default=datetime.time(21, 0)),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='start_time',
            field=models.TimeField(default=datetime.time(16, 0)),
        ),
    ]
