# Generated by Django 4.1.2 on 2022-11-08 06:57

from django.db import migrations
import shortuuid.django_fields


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0013_removalpartner_disabled"),
    ]

    operations = [
        migrations.AddField(
            model_name="customerorganisation",
            name="short_id",
            field=shortuuid.django_fields.ShortUUIDField(
                alphabet=None, length=22, max_length=40, prefix="org_"
            ),
        ),
    ]
