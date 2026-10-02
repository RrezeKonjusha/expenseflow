# Phase I: Project definition, feasibility, requirements and framework

ExpenseFlow · UBT Lab Course 2 (prof. ass. Dr. sc. Liridon Hoti) · Rreze Konjusha · Version 1.0

> **Solo exception.** The course requires teams of exactly five. The professor approved an exception for this
> project, which is built by one student. The five team roles are kept as "hats" (section 4.4), each with its own
> label on every GitHub issue, so the division of work stays visible.

## 1. Project definition

**Problem.** In small and mid-size companies, work expenses are claimed by email and Excel. Claims get lost,
nobody checks them against company policy before a manager sees them, project budgets are overrun without
warning, and there is no record of who approved what.

**Solution.** ExpenseFlow is a web platform where employees submit Travel, Meal and Equipment expenses,
department managers approve or reject them, and administrators reimburse, report and audit.

**Goals and how they are measured.**

| Goal | Measure |
| --- | --- |
| No claim gets lost | Every expense has a status (Draft, Submitted, Approved, Rejected, Reimbursed) and an audit entry per change |
| Policy is checked before approval | Per-type rules (0.40 EUR/km, 25 EUR per attendee, 1000 EUR equipment cap, 90-day age, project membership) block a submit that breaks them |
| Budgets cannot be overrun | A database trigger and CHECK constraint reject the approval that would exceed a project budget |
| Finance gets answers without Excel | Dynamic reports by date range, grouping and filters, saved and exported to CSV, XLSX, JSON |
| The system is trustworthy | HTTPS, short-lived tokens, rate limiting, account lockout, 80%+ test coverage |

**Users.** Employee (USER), department manager (MANAGER), finance or administrator (ADMIN).

**Scope.** In: the full claim lifecycle, policies, budgets, search, import/export, reports, dashboards, user and
project administration, audit log, monitoring, CI/CD, public deployment. Out: card payments, receipt upload and
OCR, multi-currency, multi-level approvals, mobile apps.

**Extra features chosen from the rubric (30%).** Four instead of the required three, as a buffer:

| # | Feature (rubric numbering) | In ExpenseFlow |
| --- | --- | --- |
| 1 | Authentication with access and refresh tokens | 15-minute access token in memory; 7-day refresh token in an httpOnly cookie, rotated and blacklisted on every use |
| 5 | Advanced search | Filters, sorting, pagination and PostgreSQL full-text search (GIN index) on expenses |
| 10 | Data export and import | Reports export to CSV, XLSX, JSON; expenses import from CSV or JSON with per-row errors |
| 11 | Dynamic reports | Report builder: date range, group by department, project, employee, type, status or month, filters; saved as MongoDB snapshots |

## 2. Technical and technological feasibility

**Verdict: feasible.** Every component is mature open-source software already integrated and running: the full
stack starts with one Docker Compose command, 82 backend tests pass with 94% coverage, and the API contract
(Newman, 42 assertions) and end-to-end tests (Cypress, 9 tests) pass on GitHub Actions.

### 2.1 Technology choices

| Layer | Choice (version) | Why it fits |
| --- | --- | --- |
| Frontend | React 18, Vite 5, Redux Toolkit 2, React Router 6, Axios, MUI 6 | Named in the course documents; component architecture, routing and state management out of the box |
| Backend | Django 5.2 LTS, Django REST Framework 3.18 | LTS with security support to April 2028; ORM, migrations, admin, validation built in |
| API docs | drf-spectacular (OpenAPI 3.0, Swagger UI) | Schema generated from code, so it cannot drift |
| Auth | djangorestframework-simplejwt 5.5 + token blacklist, django-axes 8.3 | Access/refresh rotation and brute-force lockout without custom crypto |
| SQL | PostgreSQL 16 | CHECK, DEFAULT, UNIQUE, FK cascades, triggers, PL/pgSQL procedures, full-text search |
| NoSQL | MongoDB 7 with MongoEngine 0.29 | Append-only audit log and variable-shape report snapshots with embedded documents |
| Cache, broker | Redis 7, Celery 5.6 | Dashboard cache, rate-limit counters, async email and audit writes |
| Gateway | Caddy 2 | HTTPS with automatic Let's Encrypt, reverse proxy, load balancing, security headers |
| Observability | Prometheus, Grafana, Loki + Promtail | Metrics, dashboards and centralised logs |
| Delivery | Docker Compose, GitHub Actions, GitHub Container Registry | One set of files for laptop, CI and server |
| Tests | pytest, Newman, Cypress, Locust, OWASP ZAP | Unit/integration, API contract, end-to-end, load, security |

### 2.2 Feasibility dimensions

| Dimension | Assessment |
| --- | --- |
| Technical | All mandatory pillars (frontend, backend, SQL, NoSQL) are integrated and verified by automated tests on every pull request |
| Skills | Python, JavaScript and SQL are covered by earlier courses; new tools (Celery, Caddy, MongoEngine) have extensive documentation |
| Hardware and hosting | One VPS (2 vCPU, 4 GB RAM) runs the whole stack; development needs a laptop with Docker |
| Economic | All software is free; hosting is covered by the GitHub Student Developer Pack cloud credit; a domain is available through the same pack |
| Schedule | 7 two-week sprints (section 4.3); the implementation core is already done, which leaves the remaining time for testing, deployment and documentation |
| Legal and data | Demo data only; passwords hashed (PBKDF2); no payment data is stored |

### 2.3 Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| The professor expects real microservices | High | The modules talk only through service functions, enforced by import-linter, so the reporting module can be split into its own service; Kubernetes, Kafka, gRPC and Eureka are documented as the scale-out path |
| One person carries five roles | High | Work is tracked per hat; CI gates (lint, layering, 80% coverage, e2e) replace a second reviewer |
| Email delivery fails in production | Medium | Circuit breaker (pybreaker) on SMTP, admin can activate users, Mailpit in the dev and CI stacks |
| 1000 simulated users overload one VPS | Medium | Load tests run against the local CI-mode stack; hardware is reported with the results |
| Scope creep | Medium | The "out of scope" list above; new ideas go to the backlog |

## 3. Requirements analysis

### 3.1 Elicitation

| Technique | Source | Result |
| --- | --- | --- |
| Questionnaire | 10 questions in Google Forms, sent to people who claim or approve expenses at work (`questionnaire.md`) | Results in SRS section 2 |
| Analysis of the existing process | Email with scanned receipts, Excel sheets kept by finance | Pain points: lost claims, no policy check, no budget check, no history |
| Document analysis | Course rubric and Phase I to IV requirements | Mandatory technologies, extra features, testing and deployment targets |

### 3.2 Requirements

The Software Requirements Specification (`srs.md`) lists 14 functional requirements (FR-01 to FR-14), all
priority Must, and 9 non-functional requirements (NFR-01 to NFR-09) for security, performance, scalability,
availability, maintainability, usability and portability.

Prioritisation uses MoSCoW: **Must** = the full claim lifecycle, policies, budgets, auth, search, import/export,
reports, admin, audit; **Should** = Celery worker, Prometheus and Grafana, circuit breaker, Storybook; **Could** =
WebSocket notifications; **Won't** = everything in the "out" scope above.

### 3.3 Traceability to the course requirements

| Course requirement | Where it is met |
| --- | --- |
| Frontend framework, components, Axios, routing, UI library | React SPA with 18 lazy-loaded pages, Axios interceptors, React Router with role guards, MUI |
| Backend framework, CRUD, validation, JWT | Django REST Framework, 30 API paths under `/api/v1/`, serializer and model validation, simplejwt |
| SQL database, models, relations, ORM | PostgreSQL with Django ORM: departments, users, projects, project members (N:N), polymorphic expenses |
| NoSQL database, collections | MongoDB `audit_logs` and `report_snapshots` with embedded documents |
| Git with branches, clear commits, pull requests | GitHub: `main` and `develop` protected, `feature/<issue>-name` branches, conventional commits, PRs with green CI |
| Project management tool | GitHub Issues and Projects: 78 backlog items, 7 sprint milestones, board columns To Do, In Progress, In Review, Done |

## 4. Project framework

### 4.1 Architecture

**A stateless modular monolith behind an API gateway.** Faza II allows MVC or MVVM with clearly separated
Presentation, Business Logic, Persistence and Integration layers for smaller systems. One Django API holds four
business modules plus a shared core:

| Module (Django app) | Faza II module | Owns |
| --- | --- | --- |
| `accounts` | Authentication | Register, activate, login, refresh, logout, password change and reset |
| `users` | User management | Users, departments, projects, project members |
| `expenses` | Business operations | Expense hierarchy, policies, workflow, import |
| `reporting` | Statistics and reporting | Dashboard, report builder, snapshots, export |
| `core` | Shared | Base model, permissions, audit, email adapter, error format, health check |

Every module is layered `api -> services -> selectors -> models`, and an import-linter contract in CI fails the
build if a layer or module boundary is crossed. The API keeps no session state (JWT, Redis-backed throttles), so
it runs as several replicas behind Caddy, which discovers them through Docker DNS.

**Why not microservices now.** For one developer and one domain, microservices would multiply deployment,
networking and data-consistency work without a user-visible benefit. The module boundaries are drawn so that a
module can be split into its own service later; the final report describes that path (Kubernetes and Helm,
RabbitMQ or Kafka, gRPC, Eureka or Consul).

### 4.2 Environments

| Environment | Where | How |
| --- | --- | --- |
| Local | Laptop | `docker-compose.yml` + `docker-compose.dev.yml` (hot reload, Mailpit) |
| Test and staging | GitHub Actions runner | `docker-compose.ci.yml`: the full stack is built on every pull request and tested with Newman and Cypress |
| Production | One VPS | `docker-compose.prod.yml`, deployed from `main`, HTTPS through Caddy and Let's Encrypt |

### 4.3 Methodology and schedule

Scrum with 7 two-week sprints, each a GitHub milestone:

| Sprint | Goal | Phase gate |
| --- | --- | --- |
| 1 | Foundation: repository, board, CI, SRS, questionnaire, feasibility | Phase I |
| 2 | Design: ERD, UML, component, sequence, deployment, state, DFD diagrams, Figma prototypes | Phase II |
| 3 | Authentication and administration | |
| 4 | Core business: expenses, policies, workflow, search | Phase III |
| 5 | Reporting, import/export, monitoring | |
| 6 | QA and release: load, security, test report, manuals | Parafinal presentation |
| 7 | Final report, demo video, self-evaluation | Final submission and defense |

### 4.4 Roles as hats

| Hat | Responsibilities |
| --- | --- |
| Project manager, Scrum master, QA lead | Board, sprints, SRS, questionnaire, test report, end-to-end tests, presentations |
| Backend: auth and security | `accounts`, `core`, security tests, throttling |
| Backend: business and reporting | `expenses`, `reporting`, MongoDB, import/export, load tests |
| Frontend | React app, routing, pages, Figma prototypes |
| DevOps and database | Docker, Caddy, CI/CD, VPS, PostgreSQL logic, monitoring |

Communication with the professor happens at the phase defenses and through UBT channels; there is no team chat
because there is no team.

### 4.5 Tools

| Need | Tool |
| --- | --- |
| Code and reviews | Git, GitHub pull requests with a self-review checklist |
| Tracking | GitHub Issues and Projects (see `project-management.md`) |
| CI/CD | GitHub Actions: lint, layering, tests with coverage gate, Docker test stack, image build, deploy |
| Design | PlantUML (in the repository), Figma |
| Documentation | Markdown in `docs/`, exported to one PDF |
