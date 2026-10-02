#!/usr/bin/env bash
# Nightly backup of PostgreSQL and MongoDB from a running ExpenseFlow stack.
#   scripts/backup.sh                  # production defaults
#   PROJECT=expenseflow BACKUP_DIR=./backups scripts/backup.sh
# Cron (as the deploy user, 02:00 daily):
#   0 2 * * * cd ~/expenseflow-prod && scripts/backup.sh >> ~/backups/backup.log 2>&1
set -euo pipefail

PROJECT=${PROJECT:-prod}
BACKUP_DIR=${BACKUP_DIR:-$HOME/backups}
KEEP_DAYS=${KEEP_DAYS:-7}
COMPOSE=(docker compose -p "$PROJECT" -f docker-compose.yml -f docker-compose.prod.yml)
[ -n "${COMPOSE_FILES:-}" ] && read -r -a COMPOSE <<<"docker compose -p $PROJECT $COMPOSE_FILES"
PG_USER=${POSTGRES_USER:-expenseflow}
PG_DB=${POSTGRES_DB:-expenseflow}
STAMP=$(date +%F-%H%M)

mkdir -p "$BACKUP_DIR"
# write to a temporary name first, so a failed dump never looks like a good backup
"${COMPOSE[@]}" exec -T postgres pg_dump -U "$PG_USER" -d "$PG_DB" -Fc >"$BACKUP_DIR/.pg-$STAMP.dump"
mv "$BACKUP_DIR/.pg-$STAMP.dump" "$BACKUP_DIR/pg-$STAMP.dump"
"${COMPOSE[@]}" exec -T mongo mongodump --quiet --archive --gzip --db expenseflow >"$BACKUP_DIR/.mongo-$STAMP.archive.gz"
mv "$BACKUP_DIR/.mongo-$STAMP.archive.gz" "$BACKUP_DIR/mongo-$STAMP.archive.gz"

find "$BACKUP_DIR" -maxdepth 1 \( -name 'pg-*.dump' -o -name 'mongo-*.archive.gz' \) -mtime +"$KEEP_DAYS" -delete
echo "$(date '+%Y-%m-%dT%H:%M:%S%z') backup ok: pg-$STAMP.dump ($(du -h "$BACKUP_DIR/pg-$STAMP.dump" | cut -f1)), mongo-$STAMP.archive.gz ($(du -h "$BACKUP_DIR/mongo-$STAMP.archive.gz" | cut -f1))"
