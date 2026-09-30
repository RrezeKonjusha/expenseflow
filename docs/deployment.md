# Deployment guide

## One-time server setup (about 1 hour)
1. Create an Ubuntu 24.04 droplet (2 vCPU, 4 GB) with the GitHub Student Pack credit.
2. DNS: A records `<domain>` and `staging.<domain>` to the droplet IP.
3. On the server:
   ```bash
   adduser deploy && usermod -aG docker deploy      # after installing Docker Engine
   ufw allow 22,80,443/tcp && ufw enable
   su - deploy
   git clone https://github.com/<org>/expenseflow.git ~/expenseflow-prod
   git clone -b develop https://github.com/<org>/expenseflow.git ~/expenseflow-staging
   cp ~/expenseflow-prod/.env.example ~/expenseflow-prod/.env      # edit secrets, SITE_DOMAIN=<domain>
   cp ~/expenseflow-staging/.env.example ~/expenseflow-staging/.env # SITE_DOMAIN=staging.<domain>
   ```
   Each stack binds ports 80/443, so staging and production need separate hosts. Simplest: a second small droplet
   for staging (clone only `~/expenseflow-staging` there).
4. In GitHub, create two Environments, `staging` and `production`, each with secrets `VPS_HOST`, `VPS_USER=deploy`,
   `VPS_SSH_KEY` (private key) and `DOMAIN` (same base domain in both). The deploy job picks the right set automatically.

## Every deploy (automatic)
Push to `develop` deploys staging; push to `main` deploys production (`.github/workflows/deploy.yml`):
build images, push to GHCR tagged with the commit SHA, SSH, `docker compose pull && up -d`, smoke-check `/health/`.
Migrations run automatically when the `api` container starts (`RUN_MIGRATIONS=1`).

## Environment variables
All in `.env.example`. Secrets never go into Git. Generate keys with `python -c "import secrets; print(secrets.token_urlsafe(64))"`.

## Scale out
`docker compose -p prod -f docker-compose.yml -f docker-compose.prod.yml up -d --scale api=2`.
Caddy discovers both replicas; rate limits and cache live in Redis, so replicas share them.
