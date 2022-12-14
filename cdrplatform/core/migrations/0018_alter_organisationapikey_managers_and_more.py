# Generated by Django 4.1.2 on 2022-11-09 09:40

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0017_alter_customerorganisation_options_and_more"),
    ]

    operations = [
        migrations.AlterModelManagers(
            name="organisationapikey",
            managers=[],
        ),
        migrations.AlterField(
            model_name="customerorganisation",
            name="users",
            field=models.ManyToManyField(
                related_name="organisations", to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
