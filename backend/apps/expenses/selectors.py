"""Read-side queries. Data scoping by role lives here, once."""

from django.contrib.postgres.search import SearchQuery, SearchVector
from django.db.models import Q

from .models import Expense


def expenses_visible_to(user, *, polymorphic=True):
    """USER: own. MANAGER: own + own department. ADMIN: all."""
    qs = Expense.objects.all() if polymorphic else Expense.objects.non_polymorphic()
    qs = qs.select_related("employee", "project", "decided_by", "employee__department")
    if user.is_admin:
        return qs
    if user.is_manager and user.department_id:
        return qs.filter(Q(employee=user) | Q(employee__department_id=user.department_id))
    return qs.filter(employee=user)


def search(qs, text: str):
    """Full-text search on description (uses the GIN index expense_description_fts)."""
    text = (text or "").strip()
    if not text:
        return qs
    return qs.annotate(search=SearchVector("description", config="simple")).filter(
        search=SearchQuery(text, config="simple", search_type="websearch")
    )


def can_decide(user, expense) -> bool:
    if expense.employee_id == user.pk:
        return False
    if user.is_admin:
        return True
    return user.is_manager and user.department_id is not None and expense.employee.department_id == user.department_id


def allowed_actions(user, expense) -> list[str]:
    """Transitions this user may take now. Drives the HATEOAS `_links`."""
    from .models import ExpenseStatus as S

    actions = []
    owner = expense.employee_id == user.pk
    if owner and expense.status == S.DRAFT:
        actions += ["update", "delete", "submit"]
    if owner and expense.status == S.REJECTED:
        actions.append("reopen")
    if expense.status == S.SUBMITTED and can_decide(user, expense):
        actions += ["approve", "reject"]
    return actions
