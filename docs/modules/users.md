# Module: users (User management)

**Public API:** `/api/v1/users/` (admin), `/api/v1/departments/`, `/api/v1/projects/`, `PUT /api/v1/projects/{id}/members/`.
**Entities:** User (custom, email login, role), Department, Project, ProjectMember (N:N).
**Database rules:** CHECK role, budget >= 0, spent <= budget; FK actions SET NULL / CASCADE at DB level (`migrations/0002_db_logic.py`).
**Logging and monitoring:** audit events `USER_CREATED`, `USER_UPDATED`, `USER_DEACTIVATED`, `PROJECT_MEMBERS_SET`.
**Tests:** `apps/users/tests/`.
