# Test plan and test cases

| Layer | Tool | Location | Run |
| --- | --- | --- | --- |
| Unit | pytest | `backend/apps/*/tests/test_policies.py`, `test_models.py` | `pytest` |
| Integration (every endpoint, real PostgreSQL) | pytest-django + APIClient | `backend/apps/*/tests/test_*api*.py`, `test_reports.py` | `pytest` |
| Security | pytest (`-m security`) + OWASP ZAP | `backend/apps/accounts/tests/test_security.py` | `pytest -m security` |
| API contract | Postman + Newman | `tests/postman/` | `npx newman run ...` |
| E2E | Cypress | `frontend/cypress/e2e/` | `npm run cy:run` |
| Load | Locust | `tests/locust/locustfile.py` | see file header |

Coverage gate: 80% (CI fails below). Current: 95% of `apps/` (82 backend tests, 42 Newman assertions).

## Test cases (extract, keep extending)

| ID | Layer | Scenario | Expected | Type |
| --- | --- | --- | --- | --- |
| TC-01 | Integration | Register, open email link, activate, log in | 201, activation 200, login 200 with httpOnly cookie | Happy |
| TC-02 | Integration | Reuse the activation link | 400 | Negative |
| TC-03 | Integration | Reuse an old refresh token after rotation | 401 | Security |
| TC-04 | Unit | Meal 60 EUR with 1 attendee | policy error on amount | Negative |
| TC-05 | Unit | Expense exactly 90 days old | accepted | Edge |
| TC-06 | Integration | Manager approves own department's submitted expense | 200, project.spent increases | Happy |
| TC-07 | Integration | Approve when project budget would be exceeded | 409 budget_exceeded, status unchanged | Negative |
| TC-08 | Integration | Approve a DRAFT | 409 invalid_transition | Negative |
| TC-09 | Security | Employee approves own expense | 403 | Security |
| TC-10 | Security | Manager of another department approves | 404 (not visible) | Security |
| TC-11 | Security | `q=' OR 1=1 --` | 200, no rows leaked | Security |
| TC-12 | Security | `<script>` in description | 400 | Security |
| TC-13 | Security | 6 logins in one minute | 6th returns 429 | Security |
| TC-14 | Integration | Import CSV with 2 bad rows of 5 | 3 created, errors for rows 4 and 5 | Edge |
| TC-15 | Integration | Report grouped by department, export XLSX | correct totals, valid workbook | Happy |
| TC-16 | DB | Delete parent expense row via SQL | subtype row removed (ON DELETE CASCADE) | DB |
| TC-17 | DB | `sp_mark_reimbursed(today)` | returns count of approved rows | DB |
| TC-18 | E2E | Employee creates and submits meal | status SUBMITTED in UI | Happy |
| TC-19 | Load | 1000 users, 5 min | p95 dashboard < 800 ms (cache on) | Performance |

## Report template (Faza IV)
For each run record: date, commit SHA, environment, pass/fail counts, coverage, Locust p50/p95 per endpoint (cache on vs off), ZAP findings, defects found and fixed.
