# Module: reporting (Statistics and reporting)

**Public API:** `/api/v1/reports/dashboard/`, `/run/`, `/` (list, save), `/{id}/`, `/{id}/export/?format=csv|xlsx|json`.
**Storage:** results computed from PostgreSQL; saved snapshots in MongoDB `report_snapshots` with embedded criteria and rows (denormalized so a saved report never changes).
**Caching:** dashboard per scope (all / department / user) in Redis for 5 minutes, versioned key bumped on every expense change.
**Security:** `group_by` is a whitelist; data scoped by role through `expenses.selectors`; CSV cells starting with = + - @ are escaped.
**Tests:** `apps/reporting/tests/`.
