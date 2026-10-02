#!/usr/bin/env bash
# Runs the four load scenarios: 1 and 3 API replicas, each with the Redis dashboard cache on and off.
# 1000 users, 50 new users/s, 5 minutes each. Results: results/load/<scenario>_*.csv and .html
#   LOCUST=locust tests/locust/run-matrix.sh            (run on mains power; a laptop on battery throttles)
set -euo pipefail
cd "$(dirname "$0")/../.."
LOCUST=${LOCUST:-locust}
FILES=(-f docker-compose.yml -f docker-compose.ci.yml -f tests/locust/docker-compose.load.yml)
mkdir -p results/load

run() { # name replicas cache_seconds
  local name=$1 replicas=$2 cache=$3
  echo "== $name: $replicas api replica(s), DASHBOARD_CACHE_SECONDS=$cache"
  DASHBOARD_CACHE_SECONDS=$cache docker compose "${FILES[@]}" up -d --scale api="$replicas" >/dev/null 2>&1
  docker compose "${FILES[@]}" restart api >/dev/null 2>&1 # drop any request backlog from a previous run
  for _ in $(seq 1 60); do
    healthy=$(docker compose "${FILES[@]}" ps api --format '{{.Status}}' | grep -c '(healthy)' || true)
    [ "$healthy" -eq "$replicas" ] && break
    sleep 3
  done
  echo "   healthy replicas: $healthy, cache setting: $(docker compose "${FILES[@]}" exec -T api printenv DASHBOARD_CACHE_SECONDS)"
  docker compose "${FILES[@]}" exec -T redis redis-cli flushall >/dev/null
  $LOCUST -f tests/locust/locustfile.py --host https://localhost --headless -u 1000 -r 50 -t 5m \
    --processes 4 --csv "results/load/$name" --csv-full-history --html "results/load/$name.html" --only-summary \
    >"results/load/$name.log" 2>&1
  grep -A6 '^Type     Name' "results/load/$name.log" | tail -6
}

run 1api-cache-on 1 300
run 1api-cache-off 1 0
run 3api-cache-on 3 300
run 3api-cache-off 3 0
DASHBOARD_CACHE_SECONDS=300 docker compose "${FILES[@]}" up -d --scale api=1 >/dev/null 2>&1
echo "== done"
