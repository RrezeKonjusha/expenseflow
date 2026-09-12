"""Database-level logic for the expenses module.

- Real ON DELETE actions (subtype rows cascade with their parent expense).
- trg_expense_budget: when an expense becomes APPROVED, add its amount to
  users_project.spent. The CHECK project_spent_within_budget then rejects
  approvals that would overrun the budget (API answers 409).
- trg_touch_updated_at on expenses_expense.
- sp_mark_reimbursed(p_until date): stored procedure (PL/pgSQL function)
  marking all APPROVED expenses up to a date as REIMBURSED; returns the count.
"""

from django.db import migrations

from apps.core.db import fk_actions

FK_FORWARD, FK_REVERSE = fk_actions(
    [
        ("expenses_travelexpense", "expense_ptr_id", "CASCADE"),
        ("expenses_mealexpense", "expense_ptr_id", "CASCADE"),
        ("expenses_equipmentexpense", "expense_ptr_id", "CASCADE"),
        ("expenses_expense", "employee_id", "RESTRICT"),
        ("expenses_expense", "project_id", "RESTRICT"),
        ("expenses_expense", "decided_by_id", "SET NULL"),
    ]
)

LOGIC_FORWARD = """
CREATE TRIGGER trg_touch_updated_at BEFORE UPDATE ON expenses_expense
  FOR EACH ROW EXECUTE FUNCTION fn_touch_updated_at();

CREATE OR REPLACE FUNCTION fn_expense_budget() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  IF NEW.status = 'APPROVED' AND OLD.status IS DISTINCT FROM 'APPROVED' THEN
    UPDATE users_project SET spent = spent + NEW.amount WHERE id = NEW.project_id;
  END IF;
  RETURN NEW;
END $$;

CREATE TRIGGER trg_expense_budget AFTER UPDATE OF status ON expenses_expense
  FOR EACH ROW EXECUTE FUNCTION fn_expense_budget();

CREATE OR REPLACE FUNCTION sp_mark_reimbursed(p_until date) RETURNS integer
LANGUAGE plpgsql AS $$
DECLARE
  n integer;
BEGIN
  UPDATE expenses_expense
     SET status = 'REIMBURSED', reimbursed_at = now()
   WHERE status = 'APPROVED' AND expense_date <= p_until;
  GET DIAGNOSTICS n = ROW_COUNT;
  RETURN n;
END $$;
"""

LOGIC_REVERSE = """
DROP FUNCTION IF EXISTS sp_mark_reimbursed(date);
DROP TRIGGER IF EXISTS trg_expense_budget ON expenses_expense;
DROP FUNCTION IF EXISTS fn_expense_budget();
DROP TRIGGER IF EXISTS trg_touch_updated_at ON expenses_expense;
"""


class Migration(migrations.Migration):
    dependencies = [("expenses", "0002_initial"), ("users", "0002_db_logic")]

    operations = [
        migrations.RunSQL(FK_FORWARD, FK_REVERSE),
        migrations.RunSQL(LOGIC_FORWARD, LOGIC_REVERSE),
    ]
