from django.contrib import admin
from polymorphic.admin import PolymorphicChildModelAdmin, PolymorphicParentModelAdmin

from .models import EquipmentExpense, Expense, MealExpense, TravelExpense


class ChildAdmin(PolymorphicChildModelAdmin):
    base_model = Expense


@admin.register(TravelExpense)
class TravelAdmin(ChildAdmin):
    pass


@admin.register(MealExpense)
class MealAdmin(ChildAdmin):
    pass


@admin.register(EquipmentExpense)
class EquipmentAdmin(ChildAdmin):
    pass


@admin.register(Expense)
class ExpenseAdmin(PolymorphicParentModelAdmin):
    base_model = Expense
    child_models = (TravelExpense, MealExpense, EquipmentExpense)
    list_display = ["id", "type", "employee", "project", "amount", "status", "expense_date"]
    list_filter = ["status", "type"]
