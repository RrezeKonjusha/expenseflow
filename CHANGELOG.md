# Changelog

All notable changes to ExpenseFlow. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html). Numbers in brackets are pull
requests on GitHub.

## [1.0.0] - 2026-10-02

First release: the complete expense claims and approval platform for UBT Lab Course 2.

### Added

- **Authentication** with a 15-minute access token and a 7-day refresh token in an httpOnly cookie, rotated and
  blacklisted on every use; registration with email activation, password change and reset, logout; rate limiting
  and account lockout.
- **User management**: users, departments with managers, projects with budgets and members (N:N), deactivation
  instead of deletion.
- **Expenses**: Travel, Meal and Equipment as polymorphic subtypes with their own policy; workflow draft, submitted,
  approved, rejected, reimbursed; HATEOAS `_links`; full-text search, filters, sorting, pagination; CSV and JSON
  import with per-row errors.
- **Database logic**: CHECK, DEFAULT and UNIQUE constraints, real ON DELETE CASCADE, a budget trigger that refuses
  overruns, a stored procedure for reimbursement, a GIN full-text index.
- **Reporting**: role-scoped dashboard cached in Redis, dynamic report builder, saved snapshots in MongoDB, export to
  CSV, XLSX and JSON; audit log in MongoDB with embedded documents.
- **Frontend**: React 18 SPA with 18 lazy-loaded pages, role-guarded routes, Redux Toolkit, Axios refresh
  interceptor, MUI, form validation, modals and toasts.
- **Platform**: Docker Compose stacks for development, CI and production; Caddy gateway with HTTPS and load
  balancing; Celery worker with a circuit breaker on email; Prometheus and Grafana; health checks.
- Centralised logs with Loki and Promtail (#2).
- Backend tests against real MongoDB and Redis in CI, with `real_services` integration tests (#82).
- Demo script and demo import file (#84); scripted demo rehearsal and screenshots of every page (#105).
- Phase I document, final SRS and questionnaire guide (#88); Phase II design document, diagrams and Figma
  specification (#92); defense study guide (#95); final report draft and demo video script (#96).
- Tested backup and restore scripts (#93); server bootstrap script, rollback by image tag and the deployment
  runbook (#100).
- Load test results, OWASP ZAP scans and the test report (#94); production readiness review (#98).
- Storybook with 19 stories for the shared components, built in CI (#101).
- Single documentation PDF build and a step-by-step user manual with screenshots (#107).

### Changed

- Project tracking moved from Jira to GitHub Issues and Projects (#81, #86).
- Production deploys from `main` only; the ephemeral CI Docker stack is the test and staging environment (#83).
- Django admin moved from `/admin/` to `/django-admin/` (#1).
- Vite 5 to 8 and Cypress 13 to 16; automatic code splitting cuts the first page load from 691 KB to 503 KB (#98).
- Backup scripts moved to `scripts/` (#100).

### Fixed

- `docker compose up --build` failed because two services built the same image (#1).
- The SPA's `/admin/*` pages were routed to Django admin on reload (#1).
- End-to-end tests: email timing, rotated refresh cookies, export check (#1).
- Leaving a page during a token refresh could sign the user out (#85).
- The app bar hid the product name on desktop (#91).
- `DASHBOARD_CACHE_SECONDS` was ignored, so the cache could not be switched off (#94).
- The documented production email URL (`smtp+tls://`) would stop the API from starting (#100).
- The edit page opened for expenses that are no longer drafts (#104).
- The deploy job failed on every push before a server existed (#83).

### Security

- Gateway: app shell `no-cache`, hashed assets immutable, API responses `no-store`; Cross-Origin-Opener-Policy and
  Cross-Origin-Resource-Policy `same-origin` (#94).
- Dependency audit: 3 high findings in build and test tooling removed by the Vite and Cypress upgrades; pip-audit
  clean (#98).
- Security test suite extended to expired tokens and cookie-only writes (CSRF) (#94).

[1.0.0]: https://github.com/RrezeKonjusha/expenseflow/releases/tag/v1.0.0
