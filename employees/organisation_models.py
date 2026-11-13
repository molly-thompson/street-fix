"""Organisation and employee models."""

from uuid import uuid4

from django.conf import settings
from django.db import models, transaction


class Department(models.Model):
    """An organisation unit responsible for work items."""

    name = models.CharField(max_length=150, unique=True)

    def __str__(self) -> str:
        """Return the department name."""
        return self.name


class IssueType(models.Model):
    """A kind of issue managed by a department."""

    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="issue_types",
    )
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=40)

    class Meta:
        """Order issue types by department and name."""

        constraints = [
            models.UniqueConstraint(
                fields=("department", "name"),
                name="unique_issue_type_name_per_department",
            ),
        ]
        ordering = ("department__name", "name")

    def __str__(self) -> str:
        """Return the issue type name."""
        return self.name


class Employee(models.Model):
    """An employee profile linked to a Django authentication user."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="employee_profile",
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="employees",
    )
    manager = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        related_name="direct_reports",
        null=True,
        blank=True,
    )
    email = models.EmailField(max_length=254, unique=True, null=True, blank=True)
    name = models.CharField(max_length=150)

    class Meta:
        """Order employees by display name."""

        ordering = ("name",)

    def __str__(self) -> str:
        """Return the attribution name."""
        return self.name

    @transaction.atomic
    def deactivate_and_anonymize(self) -> None:
        """Deactivate login and clear contact details while retaining attribution."""
        employee = (
            Employee.objects.select_for_update().select_related("user").get(pk=self.pk)
        )
        employee.email = None
        employee.save(update_fields=("email",))

        user = employee.user
        user.is_active = False
        user.email = ""
        user.first_name = ""
        user.last_name = ""
        user.username = f"offboarded-{uuid4().hex}"
        user.set_unusable_password()
        user.save(
            update_fields=(
                "email",
                "first_name",
                "last_name",
                "username",
                "password",
                "is_active",
            )
        )

        self.email = None
