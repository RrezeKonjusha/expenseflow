from .models import Department, Project, User


def users_list():
    return User.objects.select_related("department").all()


def departments_list():
    return Department.objects.select_related("manager").all()


def projects_visible_to(user):
    qs = Project.objects.all()
    return qs if user.is_admin else qs.filter(memberships__user=user).distinct()


def is_project_member(user_id: int, project_id: int) -> bool:
    return Project.objects.filter(pk=project_id, memberships__user_id=user_id).exists()
