# Generated by Django 3.1.5 on 2022-03-10 14:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('va_data_management', '0013_auto_20220309_2206'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicalverbalautopsy',
            name='version',
        ),
        migrations.RemoveField(
            model_name='verbalautopsy',
            name='version',
        ),
    ]
