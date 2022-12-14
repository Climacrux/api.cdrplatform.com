# Generated by Django 4.1.2 on 2022-10-23 15:33

import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="CustomerInvoice",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("invoice_id", models.CharField(max_length=10)),
                ("issued_date", models.DateField()),
                ("paid_date", models.DateField(null=True)),
                ("fees", models.PositiveIntegerField()),
                ("currency", models.CharField(max_length=3)),
                ("receiver_email", models.EmailField(max_length=254)),
                ("invoice_file", models.FileField(null=True, upload_to="")),
            ],
        ),
        migrations.CreateModel(
            name="CustomerOrganisation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("organisation_name", models.CharField(max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name="RemovalMethod",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=128)),
                ("description", models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name="RemovalPartner",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("partner_name", models.CharField(max_length=128)),
                ("description", models.TextField()),
                ("website", models.URLField()),
                ("cost_per_tonne", models.PositiveIntegerField()),
                ("currency", models.CharField(max_length=3)),
                (
                    "removal_method",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="core.removalmethod",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="RemovalRequest",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "cdr_unit",
                    models.CharField(
                        choices=[("g", "Gram"), ("kg", "Kilogram"), ("t", "Tonne")],
                        max_length=2,
                    ),
                ),
                ("requested_datetime", models.DateTimeField(auto_now_add=True)),
                ("currency", models.CharField(max_length=3)),
                ("uuid", models.UUIDField()),
                ("customer_order_id", models.CharField(blank=True, max_length=128)),
                (
                    "customer_organisation",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="core.customerorganisation",
                    ),
                ),
                (
                    "invoice",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="core.customerinvoice",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="RemovalRequestItem",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("cdr_cost", models.PositiveIntegerField()),
                ("cdr_amount", models.PositiveIntegerField()),
                (
                    "removal_partner",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="core.removalpartner",
                    ),
                ),
                (
                    "removal_request",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="core.removalrequest",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="PartnerPurchase",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("cdr_amount", models.PositiveIntegerField()),
                (
                    "cdr_unit",
                    models.CharField(
                        choices=[("g", "Gram"), ("kg", "Kilogram"), ("t", "Tonne")],
                        max_length=2,
                    ),
                ),
                ("cdr_cost", models.PositiveIntegerField()),
                ("currency", models.CharField(max_length=3)),
                ("invoice_id", models.CharField(max_length=64)),
                ("ordered_date", models.DateField(null=True)),
                ("paid_date", models.DateField(null=True)),
                ("completed_date", models.DateField(null=True)),
                ("invoice_file", models.FileField(null=True, upload_to="")),
                (
                    "removal_partner",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="core.removalpartner",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="PartnerConfirmation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("confirmation_id", models.CharField(max_length=64)),
                ("confirmation_url", models.URLField(null=True)),
                ("confirmation_file", models.FileField(null=True, upload_to="")),
                ("confirmation_image", models.ImageField(null=True, upload_to="")),
                (
                    "partner_purchase",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="core.partnerpurchase",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="customerinvoice",
            name="customer_organisation",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="core.customerorganisation",
            ),
        ),
        migrations.CreateModel(
            name="Certificate",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("certificate_id", models.CharField(max_length=11)),
                ("issued_date", models.DateField()),
                ("display_name", models.CharField(max_length=128)),
                (
                    "removal_request",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="core.removalrequest",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="CDRUser",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "name",
                    models.CharField(blank=True, max_length=150, verbose_name="name"),
                ),
                (
                    "email",
                    models.EmailField(
                        error_messages={
                            "unique": "A user with that email address already exists."
                        },
                        max_length=254,
                        unique=True,
                        verbose_name="email address",
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "verbose_name": "user",
                "verbose_name_plural": "users",
            },
            managers=[
                ("objects", django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
