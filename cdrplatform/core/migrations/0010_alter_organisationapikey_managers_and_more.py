# Generated by Django 4.1.2 on 2022-10-28 08:31

from django.db import migrations, models
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0009_organisationapikey"),
    ]

    operations = [
        migrations.AlterModelManagers(
            name="organisationapikey",
            managers=[
                ("test_objects", django.db.models.manager.Manager()),
            ],
        ),
        migrations.RenameField(
            model_name="removalrequest",
            old_name="customer_order_id",
            new_name="meta_certificate_display_name",
        ),
        migrations.AddField(
            model_name="removalrequest",
            name="meta_client_reference_id",
            field=models.CharField(blank=True, max_length=128),
        ),
        migrations.AlterField(
            model_name="organisationapikey",
            name="prefix",
            field=models.CharField(editable=False, max_length=13, unique=True),
        ),
    ]
