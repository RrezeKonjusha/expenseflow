# Software Requirements Specification: ExpenseFlow

Version 1.0 · September 2026 · Team: M1-M5 (fill in names) · UBT Lab Course 2

## 1. Introduction
**Purpose.** ExpenseFlow lets employees claim work expenses, managers approve them and admins reimburse and report on them.
**Scope.** Web application (React SPA + REST API). Out of scope: payments, receipt OCR, mobile apps, multi-currency.
**Definitions.** Expense: a claim for money spent on a project. Draft: an expense not yet submitted. Reimbursement: the company paying the claim back.

## 2. Stakeholders and elicitation
- Employees, department managers, finance/admin staff, the course professor (evaluator).
- Elicitation: online questionnaire (`questionnaire.md`, N = __ responses) and analysis of the existing process (email + Excel).
- Key findings: (fill in from responses, e.g. "68% lose track of claims sent by email").

## 3. User roles
| Role | Description |
| --- | --- |
| USER | Creates, imports and submits own expenses; sees own reports |
| MANAGER | USER rights + approves or rejects own department's expenses |
| ADMIN | Manages users, departments, projects; reimburses; sees all data and the audit log |

## 4. Functional requirements
| ID | Requirement | Priority |
| --- | --- | --- |
| FR-01 | A visitor can register; the account is activated by an emailed link | Must |
| FR-02 | A user can log in and out; sessions refresh silently | Must |
| FR-03 | A user can change and reset the password | Must |
| FR-04 | A user can create, edit and delete draft expenses of type Travel, Meal or Equipment | Must |
| FR-05 | The system enforces the expense policy per type (caps per km, per attendee, equipment max, 90-day age, project membership) | Must |
| FR-06 | A user can submit a draft; a manager of the same department or an admin can approve or reject it with a reason | Must |
| FR-07 | Approval fails if the project budget would be exceeded | Must |
| FR-08 | An admin can mark approved expenses up to a date as reimbursed | Must |
| FR-09 | Users can list, filter, sort, paginate and full-text search expenses they may see | Must |
| FR-10 | Users can import expenses from CSV or JSON and see per-row errors | Must |
| FR-11 | Users can build a report by criteria and grouping, save it and export CSV/XLSX/JSON | Must |
| FR-12 | Each role sees a dashboard with KPIs and a 6-month chart | Must |
| FR-13 | Admins manage users, departments, projects and project members | Must |
| FR-14 | Every critical action is written to an audit log that admins can browse | Must |

## 5. Non-functional requirements
| ID | Category | Requirement |
| --- | --- | --- |
| NFR-01 | Security | JWT access tokens expire after 15 min; refresh tokens rotate and are stored in httpOnly cookies |
| NFR-02 | Security | 5 login attempts per minute per IP; account locked 15 min after 5 failures |
| NFR-03 | Security | HTTPS everywhere; security headers and CSP; input validation against XSS and SQL injection |
| NFR-04 | Performance | Dashboard p95 < 800 ms with 1000 concurrent simulated users (cache on) |
| NFR-05 | Scalability | API is stateless and can run as N replicas behind the gateway |
| NFR-06 | Availability | Health endpoint for every dependency; nightly backups |
| NFR-07 | Maintainability | Layered modules enforced in CI; 80% coverage of business logic |
| NFR-08 | Usability | Responsive from 360 px; inline validation; every action confirmed with a toast |
| NFR-09 | Portability | Runs identically locally, in CI and on the server via Docker Compose |

## 6. Constraints and assumptions
React, Django, PostgreSQL, MongoDB and Docker are mandated by the team; hosting on a single VPS; team of exactly 5.

## 7. Feasibility
Technical: all components are mature open source with large communities. Economic: free tiers and student credit. Schedule: 7 two-week sprints, tracked as GitHub milestones on the project board.
