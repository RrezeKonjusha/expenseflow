# ExpenseFlow

Expense claims and approval platform for UBT Lab Course 2.
Employees submit expenses, department managers approve them, admins reimburse and report.

**Stack:** React 18 (Vite, Redux Toolkit, MUI) · Django 5.2 + DRF · PostgreSQL 16 · MongoDB 7 · Redis 7 · Celery · Caddy · Docker Compose · GitHub Actions

| What | Where |
| --- | --- |
| Backend (4 modules: accounts, users, expenses, reporting + core) | `backend/` |
| Frontend SPA | `frontend/` |
| Docker, Caddy gateway, Prometheus, Grafana, Loki + Promtail (central logs) | `docker-compose*.yml`, `infra/` |
| API contract tests (Newman), load tests (Locust) | `tests/` |
| Diagrams (PlantUML + rendered), SRS, test plan, manuals, backlog | `docs/` |
| CI/CD | `.github/workflows/` |

## Run it locally (Docker, recommended)

```bash
cp .env.example .env                    # defaults work for local dev
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
docker compose exec api python manage.py seed_demo --reset
```

| URL | What |
| --- | --- |
| https://localhost | App (accept the local certificate once) |
| https://localhost/api/docs/ | Swagger UI (OpenAPI 3.0) |
| https://localhost/django-admin/ | Django admin |
| http://localhost:8025 | Mailpit: activation and reset emails |
| http://localhost:3000 | Grafana (admin / GRAFANA_PASSWORD): metrics dashboard, logs in Explore > Loki |

Demo logins (password `Demo-Pass-2026!`): `admin@expenseflow.dev`, `besa@expenseflow.dev` (manager, Engineering),
`driton@expenseflow.dev` (manager, Sales), `arta@expenseflow.dev` (employee).

## Run without Docker (fast inner loop)

Needs PostgreSQL 16 and Redis running locally (MongoDB optional for tests: they use mongomock).

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
export DJANGO_DEBUG=1 REFRESH_COOKIE_SECURE=0 MONGO_URL=mongodb://localhost:27017/expenseflow
python manage.py migrate && python manage.py seed_demo --reset
python manage.py runserver                      # http://localhost:8000

cd ../frontend && npm install && npm run dev    # http://localhost:5173 (proxies /api to :8000)
```

## Quality gates (all run in CI)

```bash
cd backend
ruff check . && ruff format --check .   # lint
lint-imports                            # module layering contracts
pytest --cov                            # 80+ tests, coverage gate 80%
cd ../frontend && npm run lint && npm run build
npx newman run tests/postman/expenseflow.postman_collection.json -e tests/postman/local.postman_environment.json
```

## Team workflow

Solo project (approved exception to the 5-person team rule): one developer wearing five hats, shown as `hat:*` labels.

- Tracking: GitHub Issues + the GitHub Project board (To Do, In Progress, In Review, Done). Epics are parent issues
  with sub-issues, sprints are milestones (`Sprint 1` to `Sprint 7`). `docs/backlog.csv` maps the original backlog keys
  (`EXP-n`) to issue numbers.
- Branches: `feature/<issue>-short-name` from `develop`; PR into `develop` with a green CI and a self-review checklist
  comment; `develop` -> `main` at sprint end.
- Commits: Conventional Commits that reference the issue, e.g. `feat(expenses): add submit transition (#35)`.
  PR bodies say `Closes #<issue>`.

See `docs/README.md` for the documentation index.
