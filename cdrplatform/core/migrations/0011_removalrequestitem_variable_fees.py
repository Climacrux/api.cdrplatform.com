# Generated by Django 4.1.2 on 2022-10-29 09:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0010_alter_organisationapikey_managers_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="removalrequestitem",
            name="variable_fees",
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
    ]
