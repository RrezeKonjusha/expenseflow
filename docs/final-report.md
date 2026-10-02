# ExpenseFlow: final project report

UBT Lab Course 2 · prof. ass. Dr. sc. Liridon Hoti · Rreze Konjusha (solo project, approved exception) ·
Draft 1, 2 October 2026

## 1. Summary

ExpenseFlow is a web platform for work expense claims. Employees submit Travel, Meal and Equipment expenses, the
system checks company policy before submission, department managers approve or reject, the database refuses any
approval that would overrun a project budget, and finance reimburses, reports and audits. It covers all six
mandatory rubric items (React, Django, PostgreSQL, MongoDB, Git, a project-management tool) and four extra features
where three are required: access and refresh tokens, advanced search, import and export, and dynamic reports.

| Measure | Value |
| --- | --- |
| Backend | Django 5.2 + DRF, 4 business modules + core, 30 REST paths under `/api/v1/` |
| Frontend | React 18, 18 lazy-loaded pages, 3 role-specific interfaces |
| Data | PostgreSQL: 8 business tables, 14 CHECK/UNIQUE constraints, 2 triggers, 1 stored procedure; MongoDB: 2 collections with embedded documents |
| Tests | 85 backend tests, 94.18% coverage; 12 security tests; 42 API assertions; 9 end-to-end tests; 0 failures in 233,419 load-test requests |
| Process | 81 GitHub issues over 7 sprint milestones; every change through a branch, a pull request and green CI |
| Live system | `https://<domain>` (open item, section 8) |

## 2. The phases

| Phase | Deliverable | Where |
| --- | --- | --- |
| I. Definition and foundation | Project definition, feasibility, requirements analysis, framework; SRS; questionnaire; defense slides | `phase-1.md`, `srs.md`, `questionnaire.md`, Phase I deck |
| II. Design | Logical and physical architecture, ERD, UML class diagram, component, sequence, deployment, state, use case, DFD and navigation diagrams; database and NoSQL design; API design; Figma specification | `design.md`, `diagrams/`, `api/openapi.yml`, `figma-spec.md`, `design-screens/` |
| III. Implementation and validation | Four modules, gateway, cache, rate limiting, async messaging, monitoring, central logs, CI/CD, tests at every layer | `backend/`, `frontend/`, `infra/`, `.github/workflows/`, `test-report.md` |
| IV. Release | Testing and QA, deployment, technical and user documentation, presentation, this report | `test-report.md`, `deployment.md`, `maintenance.md`, `user-manual.md`, `modules/`, final deck |

### Phase I
The problem (claims lost in email and Excel, no policy or budget check, no audit trail) was confirmed by analysing the
existing process and by a stakeholder questionnaire (results: open item). Requirements: 14 functional, 9
non-functional, prioritised with MoSCoW. Framework: a stateless modular monolith, Scrum in 7 two-week sprints.

### Phase II
The architecture separates Presentation, Business Logic, Persistence and Integration in each module, with an
import-linter contract in CI that enforces the boundaries. The relational model is in third normal form, with its
rules in the database: CHECK constraints, database defaults, real ON DELETE CASCADE, a budget trigger and a
reimbursement procedure. MongoDB holds append-only and variable-shape data with calculated denormalisation; sharding
keys and write concerns are designed. Every diagram was checked against the code and the live database.

### Phase III
Implemented and integrated: JWT access and refresh tokens with rotation and blacklist; email activation and password
reset; role-based access with query scoping and HATEOAS links; polymorphic expense policies; full-text search;
CSV/JSON import with per-row errors; dynamic reports saved to MongoDB and exported to CSV, XLSX and JSON; Redis cache
and rate limiting; Celery for email and audit with a circuit breaker on SMTP; Caddy as gateway and load balancer;
Prometheus, Grafana, Loki. Validation at every layer, run on each pull request (section 4).

### Phase IV
Testing and QA, the test report, backup and restore, the deployment pipeline, the documentation set, the demo script
and video script, the final presentation and this report.

## 3. Documents and designs

| Audience | Document |
| --- | --- |
| Professor and reviewers | `phase-1.md`, `srs.md`, `design.md`, `test-report.md`, this report |
| Developers | `README.md`, `modules/*.md`, `api/openapi.yml` (Swagger at `/api/docs/`), `diagrams/` |
| Operators | `deployment.md`, `maintenance.md`, `scripts/` |
| End users | `user-manual.md` |
| Process | `project-management.md`, `backlog.csv` |
| Defense | `defense-guide.md`, `demo/README.md`, `demo/video-script.md` |

All of them are exported together as one PDF with a table of contents and the rendered diagrams.

## 4. Testing and performance

Details and reproduction steps are in `test-report.md`.

| Layer | Result |
| --- | --- |
| Unit and integration (pytest, real PostgreSQL; real MongoDB and Redis in CI) | 85 passed, 94.18% coverage, gate 80% |
| Security (SQL injection, XSS, CSRF, brute force, tokens, authorisation, headers) | 12/12 |
| API contract (Newman through the gateway over HTTPS) | 42/42 assertions |
| End-to-end (Cypress, 4 user scenarios) | 9/9 |
| Session robustness (real Chrome) | 10/10 |
| Load (Locust, 1000 users, 5 minutes) | 0 failures; cache on: median 36 ms, 431 requests/s; cache off: median 240 ms, 393 requests/s |
| OWASP ZAP baseline | Open item |

**Performance analysis.** The Redis cache makes the typical request six to eight times faster and lifts throughput by
10%. The slow tail is set by saturation: with one API replica (6 threads) the p95 stays near 1.2 s under 1000 users,
so the 800 ms target (NFR-04) is not met on one replica. The design answer is horizontal scaling, already supported
(stateless API, Caddy load balancing); the 3-replica measurement is an open item.

**Defects.** Eleven defects were found by the tests themselves and fixed, each with an issue and a pull request:
a Docker build race, a gateway route collision, three end-to-end test faults, a session lost when a page is left
mid-refresh, a hidden product name, a cache setting that could not be switched off, a CI health check, a deploy job
that failed without a server, and a demo step that would have failed on stage.

## 5. Roles as hats

The course asks for five people with defined roles. The professor approved a solo exception; the five roles are kept
as hats, each a label on every GitHub issue so the split of work is visible.

| Hat | Responsibilities | Main evidence |
| --- | --- | --- |
| Project manager, Scrum master, QA lead | Backlog, sprints, SRS, questionnaire, test report, end-to-end tests, presentations | Issues and milestones, `srs.md`, `test-report.md`, Cypress |
| Backend: auth and security | `accounts`, `core`, throttling, security tests | `accounts/`, `core/`, `test_security.py` |
| Backend: business and reporting | `expenses`, `reporting`, MongoDB, import and export, load tests | `expenses/`, `reporting/`, `tests/locust/` |
| Frontend | React app, routing, pages, Figma | `frontend/`, `figma-spec.md` |
| DevOps and database | Docker, Caddy, CI/CD, server, triggers and procedure, monitoring, backups | `docker-compose*.yml`, `infra/`, `.github/workflows/`, migrations |

Without a teammate to review code, branch protection made CI the second reviewer: nothing reaches `develop` or `main`
without lint, layering contracts, the coverage gate and the end-to-end suite passing, and each pull request carries a
written self-review.

## 6. Retrospective

**What worked**
- Putting rules in the database (CHECK, trigger, procedure) made them impossible to bypass and easy to demonstrate.
- One layered structure for every module, enforced by import-linter, kept the code navigable for one person.
- Running the full Docker stack in CI caught problems unit tests could not see: the gateway route collision and the
  image build race were both found there.
- Testing the tests: a load test that looked fine exposed a cache setting that was never read, and a real-browser
  test found a session bug the Cypress proxy hid.

**What did not**
- The first end-to-end specs were written but never run, so four defects waited until the last phase.
- Load testing on a laptop is fragile: one run was spoiled by a request backlog and one by battery throttling. Load
  tests need mains power and a separate load-generator machine.
- A full disk stopped Docker in the middle of the QA phase; a disk check belongs in the pre-test checklist.
- Jira was planned but not available; moving to GitHub Issues mid-project cost an import and a renaming of keys.

**What I would do differently**
- Run every new test the day it is written, in CI.
- Set the performance target together with the hardware it is measured on.
- Start the deployment in Sprint 1, so production problems surface early.

## 7. Recommendations and future work

| Next step | Why |
| --- | --- |
| Run 3 API replicas and repeat the load test on dedicated hardware | Meet NFR-04 (p95 < 800 ms) |
| Split `reporting` into its own service; Kafka events from `expenses`; gRPC between services; Kubernetes with Helm; Consul | The microservices path; boundaries already exist and are enforced |
| Short grace period for the previous refresh token | Remove the last case where a dropped network request signs a user out |
| Replace Promtail (end of life) with Grafana Alloy | Supported log shipping |
| Receipt upload with OCR, multi-currency, multi-level approval | The main features users asked for that were out of scope |

## 8. Open items before submission

| Item | Owner |
| --- | --- |
| Production URL, HTTPS, first deploy, backup test on production | Rreze (server and domain), then automated |
| OWASP ZAP baseline results | Rerun after Docker is restored |
| 3-replica load test | Rerun on mains power |
| Questionnaire results | Rreze collects 10 or more responses |
| Figma link and exported frames | Rreze builds from `figma-spec.md` |
| Demo video link | Rreze records from `demo/video-script.md` |
| Self-evaluation form | Rreze provides the form; answers drafted from this report |
| Phase II to IV dates | From the professor |
