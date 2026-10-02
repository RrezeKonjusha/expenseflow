# Command reference

Every command needed to run, test, demo, build and deploy ExpenseFlow. Run them from the repository root unless a
line starts with `cd`. Demo password for every seeded user: `Demo-Pass-2026!`.

## 1. Run the app locally

```bash
cp .env.example .env                                         # first time only; the defaults work locally
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build
docker compose exec api python manage.py seed_demo --reset   # demo data: 9 users, 4 projects, 154 expenses
```

| Open | What |
| --- | --- |
| https://localhost | The app (accept the local certificate once) |
| https://localhost/api/docs/ | Swagger UI, OpenAPI 3.0 |
| https://localhost/django-admin/ | Django admin (log in as `admin@expenseflow.dev`) |
| https://localhost/grafana/ | Grafana: `admin` / `GRAFANA_PASSWORD` from `.env`; logs under Explore > Loki |
| http://localhost:8025 | Mailpit: activation and password-reset emails |
| https://localhost/health/ | Health of PostgreSQL, MongoDB, Redis |

| Demo user | Role |
| --- | --- |
| `arta@expenseflow.dev` | Employee (Engineering) |
| `besa@expenseflow.dev` | Manager (Engineering) |
| `driton@expenseflow.dev` | Manager (Sales) |
| `admin@expenseflow.dev` | Admin |

```bash
docker compose ps                                            # status of every container
docker compose logs -f api worker                            # follow the API and worker logs
docker compose exec api python manage.py createsuperuser     # another admin
docker compose exec redis redis-cli flushall                 # clear cache and rate-limit counters ("Too many attempts")
docker compose -f docker-compose.yml -f docker-compose.dev.yml down        # stop (data kept)
docker compose -f docker-compose.yml -f docker-compose.dev.yml down -v     # stop and delete all data
```

The dev stack keeps the real login limit (5 per minute). If you log in many times while testing and see
"Too many attempts", run the `flushall` line above.

## 2. Backend checks and tests

One-time setup:

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
```

With the dev stack running (it exposes PostgreSQL 5432, MongoDB 27017, Redis 6379):

```bash
cd backend && source .venv/bin/activate
export DATABASE_URL=postgres://expenseflow:change-me@localhost:5432/expenseflow   # password from .env
ruff check . && ruff format --check .                        # lint and formatting
lint-imports                                                 # module layering contracts (3 kept)
DJANGO_SETTINGS_MODULE=config.settings_test python manage.py makemigrations --check --dry-run
pytest --cov                                                 # 85 passed + 5 skipped, coverage 94% (gate 80%)
pytest -m security                                           # security suite, 12 tests
TEST_MONGO_URL=mongodb://localhost:27017/expenseflow_test \
TEST_REDIS_URL=redis://localhost:6379/15 pytest              # against real MongoDB and Redis: 90 passed
pytest apps/expenses                                         # one module
pytest -k budget                                             # tests whose name contains "budget"
```

## 3. Frontend checks

```bash
cd frontend
npm ci                                                       # first time
npm run lint                                                 # ESLint
npm run build                                                # production build into dist/
npm run dev                                                  # Vite dev server on :5173 (needs the API on :8000)
npm run storybook                                            # component stories on http://localhost:6006
npm run build-storybook                                      # static Storybook, 19 stories
npm audit --omit=dev                                         # what ships to browsers
```

## 4. End-to-end tests (use the CI-mode stack)

The CI-mode stack lifts the login limit and turns off the account lockout, so the suites can log in many times.

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml down
docker compose -f docker-compose.yml -f docker-compose.ci.yml up -d --build
docker compose exec api python manage.py seed_demo --reset

# API contract, 28 requests and 42 assertions through the gateway
npx newman run tests/postman/expenseflow.postman_collection.json -e tests/postman/ci.postman_environment.json --insecure

# UI end to end, 5 specs and 10 tests in Chrome (re-seed first)
docker compose exec api python manage.py seed_demo --reset
cd frontend && npx cypress run --browser chrome              # headless
cd frontend && npx cypress open                              # interactive runner

# session survives rapid reloads (real Chrome)
cd tests/browser && npm i --no-save --no-package-lock puppeteer-core@24 && node refresh-race.mjs

# demo script rehearsal, 16 checks (re-seed and refresh the import file first)
docker compose exec api python manage.py seed_demo --reset
python3 docs/demo/make_demo_import.py && python3 tests/demo/dry_run.py

# screenshots of every page and of every Storybook story
cd tests/browser && node page-shots.mjs
cd frontend && npm run build-storybook && (cd storybook-static && python3 -m http.server 6007 &) && cd ../tests/browser && node storybook-shots.mjs
```

Inside the VS Code terminal Cypress needs `unset ELECTRON_RUN_AS_NODE` first.

## 5. Load and security tests (laptop on mains power)

```bash
# 1000 users, 1 and 3 API replicas, cache on and off; results in results/load/
pip install locust matplotlib
docker compose -f docker-compose.yml -f docker-compose.ci.yml up -d --build
tests/locust/run-matrix.sh
python tests/locust/summarize.py results/load docs/test-results/load    # tables and charts

# a single run
docker compose -f docker-compose.yml -f docker-compose.ci.yml -f tests/locust/docker-compose.load.yml up -d
locust -f tests/locust/locustfile.py --host https://localhost --headless -u 1000 -r 50 -t 5m --processes 4 --csv results/load/run

# OWASP ZAP baseline through the gateway (reports in results/zap/)
mkdir -p results/zap && chmod 777 results/zap
docker run --rm --network container:expenseflow-web-1 -v "$PWD/results/zap:/zap/wrk:rw" \
  ghcr.io/zaproxy/zaproxy:stable zap-baseline.py -t https://localhost/ -r zap-baseline.html -I

# Django production checklist and dependency audits
docker compose exec -e DJANGO_DEBUG=0 -e SECURE_HSTS_SECONDS=31536000 api python manage.py check --deploy
pip install pip-audit && pip-audit -r backend/requirements.txt
cd frontend && npm audit
```

ZAP is Java and sends no SNI for `localhost`; if the baseline cannot connect, see the `ef.localhost` setup in
`docs/test-report.md` section 5.

## 6. Documentation

```bash
scripts/build-docs.sh                                        # build/ExpenseFlow-documentation.pdf (pandoc 3, Node, Chrome)
docker run --rm -v "$PWD/docs/diagrams:/data" -w /data plantuml/plantuml -tpng -o rendered *.puml   # re-render diagrams
docker compose exec api python manage.py spectacular --file /tmp/schema.yml   # regenerate the OpenAPI schema
```

## 7. Backups (local stack or server)

```bash
# local stack
PROJECT=expenseflow COMPOSE_FILES="-f docker-compose.yml -f docker-compose.dev.yml" BACKUP_DIR=./backups scripts/backup.sh
PROJECT=expenseflow COMPOSE_FILES="-f docker-compose.yml -f docker-compose.dev.yml" BACKUP_DIR=./backups scripts/restore.sh <stamp>

# production server (as the deploy user, in ~/expenseflow-prod)
scripts/backup.sh
scripts/restore.sh 2026-10-02-0200
```

## 8. Production server (see docs/deployment.md)

```bash
# once, on a fresh Ubuntu 24.04 droplet, as root
curl -fsSL https://raw.githubusercontent.com/RrezeKonjusha/expenseflow/main/scripts/server-bootstrap.sh | bash -s -- --domain <your-domain>

# on the server, as deploy
cd ~/expenseflow-prod
docker compose -p prod -f docker-compose.yml -f docker-compose.prod.yml ps
docker compose -p prod -f docker-compose.yml -f docker-compose.prod.yml logs -f api
docker compose -p prod exec api python manage.py seed_demo --reset
docker compose -p prod -f docker-compose.yml -f docker-compose.prod.yml up -d --scale api=3   # more replicas
```

Deploys run from GitHub: merging into `main`, or Actions > Deploy > Run workflow. Rollback: the same workflow with
`image_tag` set to the commit SHA of the last good release.

## 9. Git and GitHub

```bash
git switch develop && git pull
git switch -c feature/<issue>-short-name                     # one branch per issue
git commit -m "feat(expenses): what changed (#<issue>)"
git push -u origin HEAD && gh pr create --base develop       # CI must be green, then merge
gh pr checks <pr> --watch                                    # wait for CI
gh run list -L 5                                             # recent CI and deploy runs
gh auth refresh -h github.com -s project                     # once, so the Project board can be created
```
