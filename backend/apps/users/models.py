from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.db.models import F, Q
from django.db.models.functions import Now
from django.utils import timezone

from apps.core.models import BaseModel


class Role(models.TextChoices):
    USER = "USER", "Employee"
    MANAGER = "MANAGER", "Manager"
    ADMIN = "ADMIN", "Admin"


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra):
        if not email:
            raise ValueError("Email is required")
        user = self.model(email=self.normalize_email(email).lower(), **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra):
        extra.setdefault("is_staff", False)
        extra.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra)

    def create_superuser(self, email, password=None, **extra):
        extra.update(is_staff=True, is_superuser=True, is_active=True, role=Role.ADMIN)
        return self._create_user(email, password, **extra)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.USER, db_default=Role.USER)
    department = models.ForeignKey(
        "Department", null=True, blank=True, on_delete=models.SET_NULL, related_name="members"
    )
    is_active = models.BooleanField(default=False, db_default=False)  # true after email activation
    is_staff = models.BooleanField(default=False, db_default=False)  # Django admin access only
    date_joined = models.DateTimeField(default=timezone.now, db_default=Now())

    objects = UserManager()

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "users_user"
        ordering = ["email"]
        constraints = [
            models.CheckConstraint(condition=Q(role__in=Role.values), name="user_role_valid"),
        ]

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email

    @property
    def is_admin(self):
        return self.role == Role.ADMIN

    @property
    def is_manager(self):
        return self.role == Role.MANAGER


class Department(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    manager = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="managed_departments"
    )

    class Meta:
        db_table = "users_department"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Project(BaseModel):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=150)
    budget = models.DecimalField(max_digits=12, decimal_places=2)
    spent = models.DecimalField(max_digits=12, decimal_places=2, default=0, db_default=0)  # kept by trigger
    is_active = models.BooleanField(default=True, db_default=True)
    members = models.ManyToManyField(User, through="ProjectMember", related_name="projects")

    class Meta:
        db_table = "users_project"
        ordering = ["code"]
        constraints = [
            models.CheckConstraint(condition=Q(budget__gte=0), name="project_budget_non_negative"),
            models.CheckConstraint(
                condition=Q(spent__gte=0) & Q(spent__lte=F("budget")), name="project_spent_within_budget"
            ),
        ]

    def __str__(self):
        return f"{self.code} {self.name}"


class ProjectMember(models.Model):
    """Association entity for the N:N relation User <-> Project."""

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="memberships")
    joined_at = models.DateTimeField(auto_now_add=True, db_default=Now())

    class Meta:
        db_table = "users_project_member"
        constraints = [models.UniqueConstraint(fields=["project", "user"], name="project_member_unique")]

    def __str__(self):
        return f"{self.user} in {self.project}"
