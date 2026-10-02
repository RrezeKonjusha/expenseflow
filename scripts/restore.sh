#!/usr/bin/env bash
# Restore PostgreSQL and MongoDB from one backup set (the STAMP in the file names).
#   scripts/restore.sh 2026-10-02-0200
# Stops api and worker so nothing writes during the restore, then starts them again.
set -euo pipefail

STAMP=${1:?usage: restore.sh <stamp, e.g. 2026-10-02-0200>}
PROJECT=${PROJECT:-prod}
BACKUP_DIR=${BACKUP_DIR:-$HOME/backups}
COMPOSE=(docker compose -p "$PROJECT" -f docker-compose.yml -f docker-compose.prod.yml)
[ -n "${COMPOSE_FILES:-}" ] && read -r -a COMPOSE <<<"docker compose -p $PROJECT $COMPOSE_FILES"
PG_USER=${POSTGRES_USER:-expenseflow}
PG_DB=${POSTGRES_DB:-expenseflow}
PG_FILE="$BACKUP_DIR/pg-$STAMP.dump"
MONGO_FILE="$BACKUP_DIR/mongo-$STAMP.archive.gz"
[ -s "$PG_FILE" ] && [ -s "$MONGO_FILE" ] || { echo "missing or empty backup files for $STAMP" >&2; exit 1; }

"${COMPOSE[@]}" stop api worker
trap '"${COMPOSE[@]}" start api worker >/dev/null' EXIT
"${COMPOSE[@]}" exec -T postgres pg_restore -U "$PG_USER" -d "$PG_DB" --clean --if-exists --no-owner <"$PG_FILE"
"${COMPOSE[@]}" exec -T mongo mongorestore --quiet --archive --gzip --drop <"$MONGO_FILE"
"${COMPOSE[@]}" start api worker >/dev/null
trap - EXIT
for _ in $(seq 1 30); do
  "${COMPOSE[@]}" exec -T api curl -fs http://localhost:8000/health/ >/dev/null 2>&1 && break
  sleep 2
done
echo "$(date '+%Y-%m-%dT%H:%M:%S%z') restore ok from $STAMP; health: $("${COMPOSE[@]}" exec -T api curl -s http://localhost:8000/health/)"
