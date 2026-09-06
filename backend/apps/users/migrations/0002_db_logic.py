"""Database-level rules for the users module.

- Real ON DELETE actions on foreign keys (Django only emulates them).
- fn_touch_updated_at(): shared trigger function keeping updated_at correct.
"""

from django.db import migrations

from apps.core.db import fk_actions

FK_FORWARD, FK_REVERSE = fk_actions(
    [
        ("users_user", "department_id", "SET NULL"),
        ("users_department", "manager_id", "SET NULL"),
        ("users_project_member", "project_id", "CASCADE"),
        ("users_project_member", "user_id", "CASCADE"),
    ]
)

TOUCH_FORWARD = """
CREATE OR REPLACE FUNCTION fn_touch_updated_at() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  NEW.updated_at := now();
  RETURN NEW;
END $$;

CREATE TRIGGER trg_touch_updated_at BEFORE UPDATE ON users_project
  FOR EACH ROW EXECUTE FUNCTION fn_touch_updated_at();
CREATE TRIGGER trg_touch_updated_at BEFORE UPDATE ON users_department
  FOR EACH ROW EXECUTE FUNCTION fn_touch_updated_at();
"""

TOUCH_REVERSE = """
DROP TRIGGER IF EXISTS trg_touch_updated_at ON users_project;
DROP TRIGGER IF EXISTS trg_touch_updated_at ON users_department;
DROP FUNCTION IF EXISTS fn_touch_updated_at();
"""


class Migration(migrations.Migration):
    dependencies = [("users", "0001_initial")]

    operations = [
        migrations.RunSQL(FK_FORWARD, FK_REVERSE),
        migrations.RunSQL(TOUCH_FORWARD, TOUCH_REVERSE),
    ]
