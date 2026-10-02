# Deployment guide

Environments: **local** (each laptop, `docker-compose.dev.yml`), **test/staging** (the ephemeral Docker stack the CI
e2e job builds on every pull request and push, `docker-compose.ci.yml`, where Newman and Cypress run), and
**production** (one VPS, `docker-compose.prod.yml`, deployed from `main`). There is no long-running staging server.

Server day takes under an hour: about 15 minutes of clicking, the rest is waiting for DNS and the first image build.

## 1. Buy and point (15 minutes)

1. **Server.** DigitalOcean (credit from the GitHub Student Developer Pack): Create > Droplet, Ubuntu 24.04 LTS,
   Basic, Regular, 2 vCPU / 4 GB RAM, region Frankfurt, authentication: your SSH key. Note the public IPv4.
2. **Domain.** Any registrar (the Student Pack includes a free domain through Namecheap or name.com). Pick e.g.
   `expenseflow-rreze.me`.
3. **DNS.** At the registrar, add one record and wait until it resolves (`dig +short <domain>` returns the IP):

   | Type | Host | Value | TTL |
   | --- | --- | --- | --- |
   | A | `@` | the droplet's IPv4 | 300 |

## 2. Prepare the server (one command, about 5 minutes)

```bash
ssh root@<droplet-ip>
curl -fsSL https://raw.githubusercontent.com/RrezeKonjusha/expenseflow/main/scripts/server-bootstrap.sh \
  | bash -s -- --domain <domain>
```

`scripts/server-bootstrap.sh` is idempotent (safe to run again). It installs Docker Engine and the Compose plugin,
caps container log size, adds 2 GB swap, opens only ports 22, 80 and 443, creates the `deploy` user with an SSH key
for GitHub Actions, clones the repository to `/home/deploy/expenseflow-prod`, writes `.env` with generated secrets
(mode 600) and installs the nightly backup. At the end it prints the four GitHub secrets.

Email: by default emails go to the API log (`EMAIL_URL=console://`), and an admin can activate accounts. For real
email, create a Brevo SMTP key and run the bootstrap with
`--email-url "submission://LOGIN:SMTP_KEY@smtp-relay.brevo.com:587"`, or set `EMAIL_URL` in `.env` later
(URL-encode special characters in the key).

## 3. GitHub secrets (2 minutes)

GitHub > repository > Settings > Environments > `production` > Environment secrets > Add:

| Secret | Value |
| --- | --- |
| `VPS_HOST` | the droplet's IPv4 (printed by the bootstrap) |
| `VPS_USER` | `deploy` |
| `VPS_SSH_KEY` | the private key printed by the bootstrap, including the `BEGIN` and `END` lines |
| `DOMAIN` | your domain, without `https://` |

Until `VPS_HOST` exists, every Deploy run passes with the notice "deploy is skipped".

## 4. First deploy (about 10 minutes)

GitHub > Actions > Deploy > Run workflow > branch `main` > Run. The workflow builds the `api` and `web` images, pushes
them to GitHub Container Registry tagged with the commit SHA, connects as `deploy`, pulls and starts the stack, and
checks `https://<domain>/health/` until it answers. Caddy gets the Let's Encrypt certificate on the first request;
migrations run when the `api` container starts.

Then, once, on the server:

```bash
ssh deploy@<droplet-ip>
cd ~/expenseflow-prod
docker compose -p prod exec api python manage.py seed_demo --reset   # demo data for the defense
docker compose -p prod exec api python manage.py createsuperuser       # or use admin@expenseflow.dev from the seed
```

## 5. Verify

| Check | Expected |
| --- | --- |
| `curl https://<domain>/health/` | `{"status": "ok", "checks": {"postgres": "ok", "mongo": "ok", "redis": "ok"}}` |
| Browser: `https://<domain>` | padlock, login page |
| `https://<domain>/api/docs/` | Swagger UI |
| Log in as `arta@expenseflow.dev` / `Demo-Pass-2026!` | dashboard |
| `https://<domain>/grafana/` | Grafana; user `admin`, password: `grep GRAFANA_PASSWORD ~/expenseflow-prod/.env` |
| `curl -s https://<domain>/metrics \| grep -c django_http` | `0` (metrics stay internal) |
| Demo script (`docs/demo/README.md`) | every step as written |

Test the backups once on production: `scripts/backup.sh`, then `scripts/restore.sh <stamp>` (see `maintenance.md`).

## 6. Every later deploy (automatic)

Merging `develop` into `main` (through a pull request) runs the same workflow: build, push, pull, up, smoke check.
Images are tagged with the commit SHA; images older than 7 days are pruned from the server.

## 7. Rollback

GitHub > Actions > Deploy > Run workflow > `image_tag` = the commit SHA of the last good release (from the Deploy
run history or `git log main`). Nothing is rebuilt; the server switches to those images and the smoke check runs.
If the bad release contained a database migration, also restore the backup taken before it (`maintenance.md`).

## 8. Environment variables

All of them are listed in `.env.example`; the bootstrap fills the production values. Secrets never go into Git.
To rotate a secret, edit `~/expenseflow-prod/.env` and run
`docker compose -p prod -f docker-compose.yml -f docker-compose.prod.yml up -d` (rotating `JWT_SIGNING_KEY` signs
everyone out).

## 9. Scale out

`docker compose -p prod -f docker-compose.yml -f docker-compose.prod.yml up -d --scale api=3`.
Caddy discovers every replica through Docker DNS; cache and rate limits live in Redis, so replicas share them.
