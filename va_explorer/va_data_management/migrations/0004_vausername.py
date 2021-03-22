# Generated by Django 3.1.5 on 2021-03-19 16:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('va_data_management', '0003_auto_20210222_1809'),
    ]

    operations = [
        migrations.CreateModel(
            name='VaUsername',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('va_username', models.TextField(unique=True, verbose_name='va_username')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]