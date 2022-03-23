# Generated by Django 3.0.8 on 2021-01-28 07:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("va_data_management", "0004_dhisstatus_verbalautopsy"),
    ]

    operations = [
        migrations.CreateModel(
            name="cod_codes_dhis",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("codsource", models.TextField()),
                ("codcode", models.TextField()),
                ("codname", models.TextField()),
                ("codid", models.TextField()),
            ],
        ),
    ]
