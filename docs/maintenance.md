# Maintenance and versioning

## Versioning
- Semantic versions tagged on `main` at every sprint end: `v0.<sprint>.0`; `v1.0.0` at the final defense.
- API is versioned in the URL (`/api/v1/`). Breaking changes go to `/api/v2/` while v1 keeps working.
- Database changes only through Django migrations (including RunSQL for triggers and the procedure); never edit applied migrations.

## Backups (cron on the VPS, 02:00 daily, keep 7)
```bash
docker compose -p prod exec -T postgres pg_dump -U expenseflow -Fc expenseflow > /backups/pg-$(date +%F).dump
docker compose -p prod exec -T mongo mongodump --archive --db expenseflow > /backups/mongo-$(date +%F).archive
find /backups -mtime +7 -delete
```

## Restore
```bash
docker compose -p prod exec -T postgres pg_restore -U expenseflow -d expenseflow --clean < /backups/pg-YYYY-MM-DD.dump
docker compose -p prod exec -T mongo mongorestore --archive --drop < /backups/mongo-YYYY-MM-DD.archive
```

## Rollback
Images are tagged by commit SHA: `IMAGE_TAG=<previous sha> docker compose -p prod -f docker-compose.yml -f docker-compose.prod.yml up -d`.
If the bad release contained a migration, restore the database backup taken before the deploy.

## Monitoring
- `/health/` checks PostgreSQL, MongoDB and Redis (503 when any is down).
- Grafana dashboard "ExpenseFlow API": request rate, p95 latency, status codes, DB query rate.
- Logs: `docker compose -p prod logs -f api worker` (JSON lines with `request_id` and `module`).

## Routine tasks
| Task | How |
| --- | --- |
| Create an admin | `docker compose exec api python manage.py createsuperuser` |
| Reset demo data (staging only) | `docker compose exec api python manage.py seed_demo --reset` |
| Rotate secrets | change `.env`, `docker compose up -d`; rotating `JWT_SIGNING_KEY` signs everyone out |
| Update dependencies | monthly PR: bump `requirements.txt` / `package.json`, CI must pass |
