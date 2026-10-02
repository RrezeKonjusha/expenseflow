# Production readiness review

Checked on 2 October 2026 against `develop` (eb512d3 plus this change). Every row was verified on a running stack,
not read from the configuration.

## 1. Django deployment checklist

`python manage.py check --deploy` with production settings (`DJANGO_DEBUG=0`, `SECURE_HSTS_SECONDS=31536000`,
a generated secret key):

| Check | Result | Decision |
| --- | --- | --- |
| security.W008 `SECURE_SSL_REDIRECT` not set | Warning | **Accepted.** Caddy redirects all HTTP to HTTPS (`http://localhost/` and `http://localhost/api/...` return 308 to `https://`). Django must answer plain HTTP inside the Docker network, where Caddy's upstream health check and the container health check call `http://api:8000/health/`; turning the setting on would break both. |
| security.W021 `SECURE_HSTS_PRELOAD` not set | Warning | **Accepted for now.** Joining the browser preload list is a one-way commitment for a registered domain and all its subdomains; decide once the production domain exists. HSTS itself is on: one year, include subdomains, sent by Caddy and Django. |
| axes.W006 lockout without IP address (silenced in settings) | Silenced | **Deliberate.** django-axes locks an account after 5 failures; per-IP limiting is the DRF throttle (5 login attempts per minute per IP). Locking by IP as well would lock out a whole office behind one address. |
| All other deployment checks | Pass | |

## 2. Dependency audits

| Tool | Scope | Before | After | Action |
| --- | --- | --- | --- | --- |
| pip-audit 2 | `backend/requirements.txt` | 0 known vulnerabilities | 0 | None |
| npm audit | all frontend packages | 3 high, 6 moderate | 0 high, 2 moderate | Upgraded Vite 5 to 8 (with `@vitejs/plugin-react` 6) and Cypress 13 to 16 |
| npm audit `--omit=dev` | what ships to browsers | 2 moderate | 2 moderate | Accepted, see below |

The 3 high findings were all build and test tooling, never shipped to users: the Vite development server (path
traversal) and Cypress's unzip and request libraries. They are fixed by the upgrades.

The 2 remaining moderate findings are in React Router 6 (open redirect through a backslash in `<Link>`, and a
related parsing issue). They are fixed only in React Router 7, a breaking major version. ExpenseFlow only links to
fixed internal paths and never builds a link target from user input, so the open-redirect path cannot be reached.
Upgrade to React Router 7 is listed as future work.

Upgrade side effects, all handled:

- Vite 8 (Rolldown) no longer accepts the object form of `manualChunks`; the function form pulled the data grid and
  chart libraries into every page. Automatic chunk splitting is used instead: the first page load is now 503 KB of
  JavaScript, against about 691 KB with Vite 5, and the grid and charts load only on the pages that use them.
- Cypress 16 removed `Cypress.env()`; the Mailpit address moved to `Cypress.expose()`.
- Verified after the upgrade: ESLint clean, production build, Newman 42/42, Cypress 9/9 (Cypress 16.1.1),
  real-Chrome session test 5/5.

## 3. Security settings on the running stack

| Requirement | Evidence |
| --- | --- |
| DEBUG off | `settings.DEBUG = False` |
| HSTS on | Caddy: `strict-transport-security: max-age=31536000; includeSubDomains`; Django in production: `SECURE_HSTS_SECONDS = 31536000` (`docker-compose.prod.yml`) |
| Secure cookies | `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE` and the refresh cookie all True; login response: `ef_refresh=...; HttpOnly; Path=/api/v1/auth/; SameSite=Strict; Secure` |
| CSP from Caddy | `content-security-policy: default-src 'self'; ...` on the app |
| Django admin path | `/django-admin/` redirects to its login; `/admin/users` is the SPA page (200, text/html) |
| `/metrics` not public | Through Caddy: the SPA page, 0 Prometheus lines. Inside the Docker network: 586 Prometheus lines, scraped by Prometheus only |

## 4. Fresh clone

A new clone of `develop` from GitHub, following the README word for word, as a separate Docker project with empty
volumes:

```text
cp .env.example .env
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build
  -> /health/: {"status": "ok", "checks": {"postgres": "ok", "mongo": "ok", "redis": "ok"}}
docker compose exec api python manage.py seed_demo --reset
  -> Seeded 154 expenses. Log in with any *@expenseflow.dev / Demo-Pass-2026!
POST /api/v1/auth/login/ as arta@expenseflow.dev -> 200
https://localhost/ 200 · /api/docs/ 200 · Mailpit :8025 200 · /grafana/ 200
```

One thing a new user would have tripped on, fixed: the README pointed to Grafana at `http://localhost:3000` without
the password. It now gives `https://localhost/grafana/` and says the password is `GRAFANA_PASSWORD` from `.env`.
