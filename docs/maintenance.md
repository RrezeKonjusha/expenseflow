# Maintenance and versioning

## Versioning
- Semantic versions tagged on `main` at every sprint end: `v0.<sprint>.0`; `v1.0.0` at the final defense.
- API is versioned in the URL (`/api/v1/`). Breaking changes go to `/api/v2/` while v1 keeps working.
- Database changes only through Django migrations (including RunSQL for triggers and the procedure); never edit applied migrations.

## Backups (cron on the VPS, 02:00 daily, keep 7 days)
`infra/backup/backup.sh` dumps PostgreSQL (`pg_dump -Fc`) and MongoDB (`mongodump --archive --gzip`) into
`~/backups`, writing to a temporary name first so a failed dump never looks like a good backup, and deletes sets
older than 7 days. Install the cron job once as the deploy user:
```bash
crontab -e
0 2 * * * cd ~/expenseflow-prod && infra/backup/backup.sh >> ~/backups/backup.log 2>&1
```
Copy the backups off the server now and then (for example `scp deploy@<host>:backups/* .`): a backup on the same
disk does not survive losing the droplet.

## Restore
```bash
ls ~/backups                                   # pick a set, e.g. pg-2026-10-02-0200.dump + mongo-2026-10-02-0200.archive.gz
infra/backup/restore.sh 2026-10-02-0200
```
The script stops `api` and `worker`, restores both databases (`pg_restore --clean --if-exists`,
`mongorestore --drop`), starts them again and prints `/health/`.

Tested on 2026-10-02 against the local stack: 154 expenses (sum 15431.00, GAMMA spent 2850.00), 177 audit entries
and 1 report snapshot; deleted every expense and dropped both Mongo collections; after the restore all five values
matched and `/health/` returned ok for PostgreSQL, MongoDB and Redis. Repeat the test on production once after the
first deploy (M5).

## Rollback
Images are tagged by commit SHA: `IMAGE_TAG=<previous sha> docker compose -p prod -f docker-compose.yml -f docker-compose.prod.yml up -d`.
If the bad release contained a migration, restore the database backup taken before the deploy.

## Monitoring
- `/health/` checks PostgreSQL, MongoDB and Redis (503 when any is down).
- Grafana dashboard "ExpenseFlow API": request rate, p95 latency, status codes, DB query rate.
- Logs are centralised: Promtail ships every container's output to Loki (kept 14 days). In Grafana, open Explore,
  pick the Loki datasource and query for example `{service="api", level="ERROR"}` or `{service="api"} |= "<request_id>"`.
  The dashboard "ExpenseFlow API" has a panel with all API and worker warnings and errors.
- Raw logs without Grafana: `docker compose -p prod logs -f api worker` (JSON lines with `request_id` and `module`).

## Routine tasks
| Task | How |
| --- | --- |
| Create an admin | `docker compose exec api python manage.py createsuperuser` |
| Reset demo data (staging only) | `docker compose exec api python manage.py seed_demo --reset` |
| Rotate secrets | change `.env`, `docker compose up -d`; rotating `JWT_SIGNING_KEY` signs everyone out |
| Update dependencies | monthly PR: bump `requirements.txt` / `package.json`, CI must pass |
