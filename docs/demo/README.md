# Demo script

A 10-minute live demo on production that proves every rubric line. Three browser profiles are signed in
beforehand (arta, besa, admin), so no passwords are typed on stage.

## Before the demo

1. `python docs/demo/make_demo_import.py` (expenses older than 90 days are rejected, so the file needs fresh dates).
2. `docker compose exec api python manage.py seed_demo --reset` on the stack you demo from.
3. Open tabs: the app, `/api/docs/`, Mailpit (local stack) or the inbox (production), Grafana, the latest green
   GitHub Actions run, the GitHub Project board, one merged pull request.

Seed data: departments Engineering, Sales, Finance; `admin@expenseflow.dev`, managers `besa@` (Engineering) and
`driton@` (Sales), six employees including `arta@` (Engineering); projects ALPHA, BETA, GAMMA, DELTA with GAMMA at
about 95% of its budget; about 150 expenses over the last 6 months in every status; one saved report
"Last 90 days by department". Password for every demo user: `Demo-Pass-2026!`.

## Steps

| # | As | Action | Proves |
| --- | --- | --- | --- |
| 1 | guest | Open the live URL (padlock) and `/api/docs/` | HTTPS, OpenAPI 3.0, `/api/v1` |
| 2 | new user | Register, open the activation email, activate, log in | Email service, activation, JWT |
| 3 | arta | New Meal expense, 1 attendee, 60 EUR: inline error, then the server policy error; change to 3 attendees; save; submit; toast | Dynamic validation, polymorphic policy, state change |
| 4 | arta | Import [`demo-import.csv`](demo-import.csv): 4 drafts created, row 5 rejected ("Meals are capped at 25.00 EUR per attendee") | Extra feature 10 (import) |
| 5 | arta | Reload the page, show `POST /auth/refresh/` in the Network tab and the httpOnly cookie | Extra feature 1 (access + refresh token) |
| 6 | arta | In Swagger, call approve on her own expense: 403 | Authorization |
| 7 | besa | Approvals: filter and full-text search "hotel"; approve one; approve a GAMMA expense: "Project GAMMA budget would be exceeded" | Extra feature 5 (search), DB trigger + CHECK |
| 8 | admin | Dashboard; Report builder: last quarter, group by department, status APPROVED; chart; save; export XLSX and open it | Extra features 10 and 11, MongoDB snapshot, Redis cache |
| 9 | admin | Reimburse approved expenses until today ("N expenses reimbursed"); open the Audit log and expand an entry | Stored procedure, audit trail, embedded documents |
| 10 | any | Grafana metrics panel and Loki logs, `/health/`, green GitHub Actions run, GitHub Project board, a merged PR with its self-review | Monitoring, logging, CI/CD, Git, project management |
| 11 | slides | Coverage %, Cypress video, Locust chart, ZAP summary | Testing |

## Rehearsal check

`python tests/demo/dry_run.py` runs steps 1, 3, 4, 6, 7, 8, 9 and 10 through the API against a freshly seeded stack
and checks each documented outcome; steps 2 and 5 are covered by Cypress spec 1 and `tests/browser/refresh-race.mjs`.
Last run (2 October 2026, local stack): **16/16 checks as written**: the import created 4 and rejected row 5, the
GAMMA approval returned "Project GAMMA budget would be exceeded (budget 3000.00, spent 2850.00, this expense
190.00)", and the reimbursement run marked 21 expenses.

Difference from the original design document (section 14): step 3 there fixes the 60 EUR meal with 2 attendees,
which still breaks the 25 EUR per attendee cap (2 x 25 = 50). This script uses 3 attendees.

## Fallbacks

If email is slow, show the message in Mailpit on the local stack. If the network fails, run the same script on the
local stack (`docker-compose.dev.yml`). Keep the demo video ready.
