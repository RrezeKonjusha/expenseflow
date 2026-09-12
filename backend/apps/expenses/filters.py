from django_filters import rest_framework as filters

from .models import Expense, ExpenseStatus, ExpenseType
from .selectors import search


class ExpenseFilter(filters.FilterSet):
    status = filters.MultipleChoiceFilter(choices=ExpenseStatus.choices)
    type = filters.MultipleChoiceFilter(choices=ExpenseType.choices)
    project = filters.NumberFilter(field_name="project_id")
    employee = filters.NumberFilter(field_name="employee_id")
    department = filters.NumberFilter(field_name="employee__department_id")
    date_from = filters.DateFilter(field_name="expense_date", lookup_expr="gte")
    date_to = filters.DateFilter(field_name="expense_date", lookup_expr="lte")
    amount_min = filters.NumberFilter(field_name="amount", lookup_expr="gte")
    amount_max = filters.NumberFilter(field_name="amount", lookup_expr="lte")
    q = filters.CharFilter(method="filter_q", label="Full-text search in description")
    mine = filters.BooleanFilter(method="filter_mine", label="Only my own expenses")

    class Meta:
        model = Expense
        fields = []

    def filter_q(self, qs, name, value):
        return search(qs, value)

    def filter_mine(self, qs, name, value):
        return qs.filter(employee=self.request.user) if value else qs
