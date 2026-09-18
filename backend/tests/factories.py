from datetime import timedelta
from decimal import Decimal

import factory
from django.utils import timezone

from apps.expenses.models import EquipmentExpense, MealExpense, TravelExpense
from apps.users.models import Department, Project, ProjectMember, User

PASSWORD = "Str0ng-Pass-123"


class DepartmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Department
        django_get_or_create = ["name"]

    name = factory.Sequence(lambda n: f"Dept {n}")


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True

    email = factory.Sequence(lambda n: f"user{n}@test.dev")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    is_active = True
    role = "USER"
    password = factory.PostGenerationMethodCall("set_password", PASSWORD)

    @factory.post_generation
    def _save(obj, create, extracted, **kwargs):
        if create:
            obj.save()


class ProjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Project
        skip_postgeneration_save = True

    code = factory.Sequence(lambda n: f"P{n:03d}")
    name = factory.Faker("bs")
    budget = Decimal("10000.00")

    @factory.post_generation
    def members(obj, create, extracted, **kwargs):
        for user in extracted or []:
            ProjectMember.objects.create(project=obj, user=user)


def _recent():
    return timezone.localdate() - timedelta(days=3)


class MealFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MealExpense

    amount = Decimal("40.00")
    attendees = 2
    expense_date = factory.LazyFunction(_recent)
    description = "Team lunch with client"


class TravelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TravelExpense

    amount = Decimal("30.00")
    distance_km = Decimal("100.0")
    destination = "Prizren"
    expense_date = factory.LazyFunction(_recent)
    description = "Client visit by car"


class EquipmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EquipmentExpense

    amount = Decimal("250.00")
    item_name = "Monitor"
    serial_no = "SN-123"
    expense_date = factory.LazyFunction(_recent)
    description = "External monitor"
