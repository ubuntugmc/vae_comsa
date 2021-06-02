# Generated by Django 3.1.5 on 2021-05-28 14:12

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_merge_20210210_0136'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, null=True),
        ),
    ]