# Generated by Django 3.1.5 on 2022-02-25 20:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('va_data_management', '0012_merge_20220225_2049'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalverbalautopsy',
            name='Id10011',
            field=models.TextField(blank=True, verbose_name='Time at start of interview'),
        ),
        migrations.AlterField(
            model_name='verbalautopsy',
            name='Id10011',
            field=models.TextField(blank=True, verbose_name='Time at start of interview'),
        ),
    ]
