# Generated by Django 4.1.2 on 2022-10-24 11:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_alter_cdruser_managers_removalmethod_slug_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="removalpartner",
            old_name="partner_name",
            new_name="name",
        ),
    ]
