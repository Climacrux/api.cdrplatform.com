# Generated by Django 4.1.2 on 2022-10-25 13:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0007_alter_removalrequest_uuid"),
    ]

    operations = [
        migrations.RenameField(
            model_name="partnerpurchase",
            old_name="cdr_unit",
            new_name="weight_unit",
        ),
        migrations.RenameField(
            model_name="removalrequest",
            old_name="cdr_unit",
            new_name="weight_unit",
        ),
    ]
