# Module: expenses (Business operations)

**Public API:** `/api/v1/expenses/` CRUD, `/{id}/submit|approve|reject|reopen/`, `/reimburse/`, `/import/`.
**Domain:** `Expense` (polymorphic base) with `TravelExpense`, `MealExpense`, `EquipmentExpense`; policies in `policies.py` (pure functions); state machine methods on the model; HATEOAS `_links` from `selectors.allowed_actions`.
**Database logic:** `migrations/0003_db_logic.py`: `trg_expense_budget`, `trg_touch_updated_at`, `sp_mark_reimbursed(date)`, CASCADE on subtype tables; GIN full-text index.
**Logging and monitoring:** audit events `EXPENSE_*`, `EXPENSES_IMPORTED`, `EXPENSES_REIMBURSED`; dashboard cache invalidated on every transition.
**Tests:** `apps/expenses/tests/` (policies, model + DB rules, API).
