from django.db import transaction

from apps.core import audit

from .models import Project, ProjectMember, User


@transaction.atomic
def create_user(*, by, request=None, password, **fields) -> User:
    user = User.objects.create_user(password=password, is_active=fields.pop("is_active", True), **fields)
    audit.record("USER_CREATED", actor=by, target=user, request=request)
    return user


@transaction.atomic
def update_user(user: User, *, by, request=None, **fields) -> User:
    changes = {}
    for key, value in fields.items():
        if key == "password":
            if value:
                user.set_password(value)
                changes["password"] = ("***", "***")
            continue
        old = getattr(user, key)
        if old != value:
            changes[key] = (getattr(old, "pk", old), getattr(value, "pk", value))
            setattr(user, key, value)
    user.save()
    if changes:
        audit.record("USER_UPDATED", actor=by, target=user, changes=changes, request=request)
    return user


def deactivate_user(user: User, *, by, request=None) -> None:
    user.is_active = False
    user.save(update_fields=["is_active"])
    audit.record("USER_DEACTIVATED", actor=by, target=user, request=request)


@transaction.atomic
def set_project_members(project: Project, user_ids: list[int], *, by, request=None) -> Project:
    current = set(project.memberships.values_list("user_id", flat=True))
    wanted = set(user_ids)
    ProjectMember.objects.filter(project=project, user_id__in=current - wanted).delete()
    ProjectMember.objects.bulk_create([ProjectMember(project=project, user_id=uid) for uid in wanted - current])
    audit.record(
        "PROJECT_MEMBERS_SET",
        actor=by,
        target=project,
        changes={"members": (sorted(current), sorted(wanted))},
        request=request,
    )
    return project
