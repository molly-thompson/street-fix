"""Seed the fixed report contact methods."""

from django.db import migrations


CONTACT_METHODS = (
    ("EMAIL", "Email"),
    ("TELEPHONE", "Telephone"),
    ("POST", "Post"),
)


def seed_contact_methods(apps, schema_editor):
    """Create the fixed contact methods with their default labels."""
    ContactMethod = apps.get_model("intake", "ContactMethod")
    ContactMethod.objects.bulk_create(
        [
            ContactMethod(code=code, label=label)
            for code, label in CONTACT_METHODS
        ]
    )


def unseed_contact_methods(apps, schema_editor):
    """Remove only the seeded contact methods when reversing this migration."""
    ContactMethod = apps.get_model("intake", "ContactMethod")
    ContactMethod.objects.filter(code__in=[code for code, _ in CONTACT_METHODS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("intake", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_contact_methods, unseed_contact_methods),
    ]
