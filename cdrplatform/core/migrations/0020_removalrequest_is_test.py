# Generated by Django 4.1.3 on 2022-11-29 19:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0019_alter_partnerconfirmation_confirmation_url"),
    ]

    operations = [
        migrations.AddField(
            model_name="removalrequest",
            name="is_test",
            field=models.BooleanField(default=True),
        ),
    ]
