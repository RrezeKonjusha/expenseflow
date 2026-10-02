# Defense study guide

For Rreze Konjusha, before each phase defense. Read one module per sitting, cover the answers, say them out loud, then
check. Every answer points at the file that proves it, so you can open it on screen if asked.

## 0. The 60-second pitch

ExpenseFlow replaces expense claims by email and Excel. Employees submit Travel, Meal or Equipment expenses; the
system checks company policy before anyone sees them; department managers approve or reject; the database itself
refuses any approval that would overrun a project budget; finance reimburses with one stored procedure, builds
reports and exports them; every critical action lands in an audit log in MongoDB. It is a stateless modular monolith:
React in front, one Django REST API with four modules behind a Caddy gateway, PostgreSQL, MongoDB and Redis, all in
Docker Compose, tested on every pull request and deployed from GitHub Actions. I built it alone under an approved
exception, wearing five hats that are tracked on every GitHub issue.

## 1. The ten questions most likely to come

**Q1. Why a modular monolith and not microservices?**
Faza II allows MVC with clear Presentation, Business, Persistence and Integration layers for smaller systems. For one
developer and one business domain, microservices would add separate deployments, network calls, distributed
transactions and eventual consistency between services, with no benefit a user would see. I still drew service-ready
boundaries: four modules, each with its own API, services, selectors and models, and an import-linter contract in CI
that fails the build if one module reaches into another's internals (`backend/pyproject.toml`). The API keeps no
session state, so it already scales horizontally: `docker compose up --scale api=3` and Caddy balances across the
replicas. Splitting `reporting` out would be the first step (section 9).

**Q2. How do the access and refresh tokens work, and what is rotation?**
Login returns a 15-minute access token in the JSON body and sets a 7-day refresh token as an httpOnly, Secure,
SameSite=Strict cookie limited to `/api/v1/auth/` (`accounts/api/views.py`, `_set_refresh_cookie`). The SPA keeps the
access token only in memory (Redux), never in localStorage, so JavaScript injected by an attacker cannot read a
long-lived token. When the access token expires the Axios interceptor calls `/auth/refresh/` once; the server
validates the cookie, issues a new access token and a **new** refresh token, and blacklists the old one
(`ROTATE_REFRESH_TOKENS` and `BLACKLIST_AFTER_ROTATION` in `settings.py`). If a stolen refresh token is used after the
real user has refreshed, it is already blacklisted and returns 401: reuse is detected. Test:
`test_refresh_rotation_and_reuse_detection`. Logout blacklists the token and deletes the cookie.

**Q3. How is polymorphism implemented?**
`Expense` is the base class with the shared fields and the state machine (`expenses/models.py`). `TravelExpense`,
`MealExpense` and `EquipmentExpense` inherit from it, each in its own table joined 1:1 by `expense_ptr_id`
(multi-table inheritance). `Expense.policy_violations()` merges the common rules with `self.type_violations()`. The
base version raises `NotImplementedError`; every subclass overrides it with its own rule: 0.40 EUR per km, 25 EUR per
attendee, 1000 EUR and a serial number for equipment. `MealExpense` also overrides `reimbursable_amount()`.
django-polymorphic makes `Expense.objects.all()` return the real subclasses, so a service calls one method on "an
expense" and the right rule runs. That is runtime polymorphism (late binding). `BaseModel` in `core/models.py` is the
abstract entity: no table, only `created_at` and `updated_at`.

**Q4. Why MongoDB for the audit log and report snapshots?**
Audit entries are append-only, numerous and differently shaped per action (a login has no field changes, an update
has several). A saved report's rows depend on its grouping. Neither is joined back into relational queries. So they
fit documents with embedded parts: `actor`, `target` and `changes` inside an audit entry (`core/documents.py`),
`owner`, `criteria`, `rows` and `totals` inside a snapshot (`reporting/documents.py`). The actor's email and role are
copied in at write time (denormalisation), so the history stays true after a user changes role. PostgreSQL stays the
source of truth; nothing the business rules depend on lives in MongoDB.

**Q5. How do the trigger and the stored procedure work?**
`trg_expense_budget` is an AFTER UPDATE OF status trigger on `expenses_expense`. When the status becomes APPROVED, it
adds the amount to `users_project.spent`. `users_project` has `CHECK (spent <= budget)`, which PostgreSQL evaluates in
the same transaction, so an approval that would overrun the budget fails inside the database. The service catches
that `IntegrityError` and answers 409 with "Project X budget would be exceeded" (`expenses/services.py`,
`_transition`). Because it is in the database, no other path (admin, SQL, a future service) can bypass it.
`sp_mark_reimbursed(p_until date)` is a PL/pgSQL function: one set-based UPDATE of every APPROVED expense up to the
date, returning the row count via `GET DIAGNOSTICS`. The admin's Reimburse button calls it with a bound parameter
(`reimburse_until`). Both live in migrations (`expenses/migrations/0003_db_logic.py`). Tests:
`test_trigger_blocks_budget_overrun`, `test_stored_procedure_reimburses`.

**Q6. How is CSRF handled?**
CSRF works because a browser attaches cookies to a cross-site request automatically. The API does not authenticate
with cookies: every protected endpoint needs an `Authorization: Bearer` header, which a browser never adds on its own
and another site cannot set. The one cookie, the refresh token, is SameSite=Strict, so the browser does not send it
from another site at all, and its path is only `/api/v1/auth/`. Even holding that cookie, you cannot write data:
`test_cookie_alone_cannot_write` logs in, keeps only the cookie and gets 401 on POST.

**Q7. How do you stop SQL injection and XSS?**
SQL: all queries go through the Django ORM, which binds parameters; the only raw SQL is in migrations and the procedure
call, which also binds its parameter. The full-text search builds a `SearchQuery`, not a string. Test: three classic
payloads in `?q=` return 200 and no rows. XSS: serializers reject `<` and `>` in every free-text field (`no_html` in
`users/api/serializers.py`), React escapes everything it renders, and Caddy sends a Content-Security-Policy of
`default-src 'self'`. Exports neutralise cells that start with `=`, `+`, `-` or `@` against spreadsheet formula
injection.

**Q8. How does authorisation work for the three roles?**
Two layers. Permission classes check the role (`core/permissions.py`: `IsAdmin`, `IsManagerOrAdmin`). Selectors scope
every query by role (`expenses/selectors.py`, `expenses_visible_to`): a user sees their own, a manager their
department, an admin everything. An expense outside your scope is not in your queryset, so you get 404, not 403, and
you cannot even learn that it exists. Decisions use `can_decide`: never your own expense, admin always, manager only
for their department. The role claim in the JWT is informational; the server reads the user and role from the
database on every request, so a role change applies immediately.

**Q9. How do you know it works? What is your test coverage?**
85 backend tests at 94% coverage with a CI gate at 80%; the same suite runs against real MongoDB and Redis in CI.
12 security tests. A Postman collection with 42 assertions runs through the gateway with Newman, 4 Cypress specs
(9 tests) drive the real UI, and a real-Chrome test checks that sessions survive rapid reloads. All of them run on
every pull request, and `main` and `develop` cannot merge without them. Load: 1000 users for 5 minutes, 0 failures.

**Q10. What did the load test show?**
With 1000 users, the Redis cache cut the median response from 230 to 30 ms and raised throughput 10%. Even uncached
endpoints got faster, because the dashboard stopped holding the shared workers. The p95 stayed near 1.2 s in both runs
on one API replica, so the 800 ms target is not met yet: one container with 6 threads is saturated. The fix is the one
the architecture was built for, more replicas behind Caddy; that run is the next measurement (`test-report.md`).

## 2. Module: accounts (authentication)

| File | What it does |
| --- | --- |
| `api/views.py` | Register, activate, login, refresh, logout, me, password change/forgot/reset. Sets and clears the refresh cookie. |
| `api/serializers.py` | `LoginSerializer` adds `role`, `department_id`, `email` claims; input validation for every auth form |
| `services.py` | Use cases: register (inactive user + email), activate, password flows, logout (blacklist) |
| `tokens.py` | Activation token: signed, stateless, single use because it hashes `is_active` |
| `tests/test_auth_api.py`, `tests/test_security.py` | Auth flows; the security suite |

- *Why is an activation link single use?* The token hash includes `is_active`; once the account is active the hash no
  longer matches. No table needed.
- *What stops brute force?* A 5-per-minute throttle on login and password endpoints (Redis counters) and django-axes,
  which locks the account after 5 failures for 15 minutes.
- *Why does forgot-password always answer the same?* So nobody can find out which emails have accounts.
- *What happens on password change?* Every refresh token of that user is blacklisted (`test_change_password_revokes_sessions`).

## 3. Module: users (user management)

| File | What it does |
| --- | --- |
| `models.py` | `User` (email login, role, department), `Department` (with manager), `Project` (budget, spent), `ProjectMember` (N:N with `joined_at`) |
| `api/views.py`, `serializers.py` | Admin CRUD for users, departments, projects; `PUT projects/{id}/members/` |
| `services.py` | Create user, deactivate instead of delete, membership changes, each audited |
| `selectors.py` | `is_project_member` and other read helpers used by other modules |
| `migrations/0002_db_logic.py` | CHECK constraints, real ON DELETE CASCADE on memberships, the touch trigger |

- *Why does DELETE deactivate?* Expenses keep a RESTRICT foreign key to their employee; history must survive.
- *Where is the N:N?* User and Project through `ProjectMember`, with a UNIQUE (project, user) constraint.

## 4. Module: expenses (business operations)

| File | What it does |
| --- | --- |
| `models.py` | The hierarchy and the state machine (`submit`, `approve`, `reject`, `reopen`) |
| `policies.py` | Pure functions for the rules; no database, unit-tested on their own |
| `services.py` | Each use case in one transaction, one audit entry, one cache bump; the procedure call; import |
| `selectors.py` | Role scoping, full-text search, `can_decide`, the HATEOAS action list |
| `api/serializers.py` | One serializer for all types; `type` picks the subtype; builds `_links` |
| `filters.py` | Filters, date and amount ranges, `q` full-text |
| `migrations/0003_db_logic.py` | Trigger, procedure, GIN index, cascades |
| `management/commands/seed_demo.py` | Demo data, GAMMA at 95% of its budget |

- *What is HATEOAS here?* Every expense carries `_links` with only the actions you may take now; the UI draws its
  buttons from them, so the rules exist once, on the server.
- *How does import report errors?* Each row is validated like a normal create; valid rows are saved as drafts,
  invalid ones come back as `{row, errors}`.
- *Why can't a manager approve their own expense?* Twice enforced: `can_decide` returns false, and `approve()` raises.

## 5. Module: reporting (statistics and reporting)

| File | What it does |
| --- | --- |
| `services.py` | Dashboard per scope with Redis cache; dynamic reports (whitelisted `group_by`, filters); snapshots; CSV/XLSX/JSON export |
| `documents.py` | `ReportSnapshot` with embedded `Owner`, `Criteria`, `Row`, `Totals` |
| `api/views.py` | Dashboard, run, save, list, delete, export, audit log |

- *How is the cache invalidated?* A version number in Redis is part of every dashboard key; each expense change
  increments it, so old entries are never read again and expire on their own (300 s).
- *How are reports "dynamic" but safe?* Criteria are validated and `group_by` is a whitelist mapped to ORM
  expressions, so user input never becomes SQL.

## 6. Module: core (shared)

| File | What it does |
| --- | --- |
| `models.py` | `BaseModel`, the abstract entity |
| `permissions.py` | Role permission classes |
| `exceptions.py` | Domain errors and the one error format `{type, detail, errors}` |
| `audit.py`, `documents.py`, `tasks.py` | Audit API, MongoDB document, Celery task that writes it (synchronously if the broker is down) |
| `integrations/email.py` | Email through Celery with a circuit breaker: after 3 SMTP failures it fails fast for 60 s |
| `middleware.py`, `logging.py` | Request ID on every request and response; JSON logs with module and request ID |
| `views.py` | `/health/`: PostgreSQL, MongoDB, Redis; 503 if any is down |

- *What is a circuit breaker for?* So a dead mail server does not make every request hang; requests fail fast and
  the system recovers on its own.

## 7. Databases

- *Normal forms?* Third normal form: no repeated groups, every non-key field depends on the whole key and only on it.
  `spent` is the one deliberate derived value, kept by the trigger for speed and for the CHECK.
- *Indexes?* status; (employee, date DESC) for "my expenses"; (project, status) for budgets and reports; GIN on the
  description for full-text search; one per foreign key.
- *Sharding?* Designed, not needed yet: hashed `actor.user_id` for audit logs, `owner.user_id` for snapshots.
- *Consistency?* Audit writes are eventual (via Celery, server-default acknowledgement); snapshots use
  `w: "majority"`.

## 8. Frontend, DevOps, process

- *State management?* Redux Toolkit for the session only; page data is fetched per page with Axios.
- *Routing?* React Router, nested and lazy-loaded, with `RequireAuth roles=[...]` guards.
- *What does CI do?* Lint (ruff, ESLint), layering contracts, migrations check, tests with the coverage gate against
  real databases, frontend build, then builds the whole Docker stack and runs Newman, Cypress and the browser test.
- *How do you deploy?* Merge to `main`: images built and pushed to GHCR tagged with the commit, SSH to the VPS,
  `docker compose pull && up -d`, migrations run on start, smoke check on `/health/`. Rollback = previous tag.
- *Monitoring?* Prometheus scrapes every replica, Grafana dashboard; Loki and Promtail collect every container's logs.
- *Backups?* Nightly `pg_dump` and `mongodump`, 7 days kept, restore script tested by deleting everything.
- *How did you work alone?* GitHub Issues with epics, sprints as milestones, a `hat:` label per role, a branch and pull
  request per issue with a self-review checklist, and branch protection so CI acts as the second reviewer.

## 9. Future work: the microservices path (answers when asked)

| Piece | Why not now | How it would be added |
| --- | --- | --- |
| **Kubernetes + Helm** | One VPS and Compose already give replicas, restarts and health checks; K8s adds a control plane to operate | One Deployment per container, Services for discovery, an Ingress replacing Caddy, a Horizontal Pod Autoscaler on CPU, rolling updates; a Helm chart templating it per environment; CI runs `helm upgrade` instead of `compose up` |
| **RabbitMQ or Kafka** | Celery on Redis already does the async work (emails, audit) | Celery can switch its broker to RabbitMQ with one setting; Kafka when other services need the event stream: expenses would publish `ExpenseApproved` and reporting and audit would consume it |
| **gRPC** | Modules call each other in-process; a network call would only add latency | Once `reporting` is its own service, define a `.proto` for "expenses visible to user X" and call it with gRPC instead of importing the selector |
| **Eureka or Consul** | Docker DNS plus Caddy's dynamic upstreams already find every replica on one host | On several hosts, services register with Consul and Caddy or the K8s Service reads from it |
| **Circuit breaker everywhere** | Only SMTP is remote today (pybreaker) | Wrap every service-to-service call the same way |

The first split would be `reporting`: it only reads expenses (through selectors) and writes MongoDB, so it can move
behind its own API with the least change. The import-linter contracts already prove nobody depends on its internals.

## 10. Live demo commands

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build
docker compose exec api python manage.py seed_demo --reset
open https://localhost  /api/docs/  http://localhost:8025  http://localhost:3000
cd backend && pytest --cov && pytest -m security
```
Demo users: `admin@`, `besa@` (manager), `arta@` (employee) at `expenseflow.dev`, password `Demo-Pass-2026!`.
The step-by-step demo is in `docs/demo/README.md`.
