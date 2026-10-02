# Deployment guide

Environments: **local** (each laptop, `docker-compose.dev.yml`), **test/staging** (the ephemeral Docker stack the CI
e2e job builds on every PR and push, `docker-compose.ci.yml`, where Newman and Cypress run), and **production**
(one VPS, `docker-compose.prod.yml`, deployed from `main`). There is no long-running staging server: one VPS only
needs one set of ports 80/443, and the CI stack runs the same images and compose files on every change.

## One-time server setup (about 1 hour)
1. Create an Ubuntu 24.04 droplet (2 vCPU, 4 GB) with the GitHub Student Pack credit.
2. DNS: an A record for `<domain>` (and optionally `www`) to the droplet IP.
3. On the server:
   ```bash
   adduser deploy && usermod -aG docker deploy      # after installing Docker Engine
   ufw allow 22,80,443/tcp && ufw enable
   su - deploy
   git clone https://github.com/RrezeKonjusha/expenseflow.git ~/expenseflow-prod
   cp ~/expenseflow-prod/.env.example ~/expenseflow-prod/.env      # edit secrets, SITE_DOMAIN=<domain>
   ```
4. In GitHub, Settings > Environments > `production`: add secrets `VPS_HOST`, `VPS_USER=deploy`,
   `VPS_SSH_KEY` (private key) and `DOMAIN`. Until `VPS_HOST` exists the deploy job skips with a notice.

## Every deploy (automatic)
Merging `develop` into `main` deploys production (`.github/workflows/deploy.yml`); `develop` is only tested, in the CI stack:
build images, push to GHCR tagged with the commit SHA, SSH, `docker compose pull && up -d`, smoke-check `/health/`.
Migrations run automatically when the `api` container starts (`RUN_MIGRATIONS=1`).

## Environment variables
All in `.env.example`. Secrets never go into Git. Generate keys with `python -c "import secrets; print(secrets.token_urlsafe(64))"`.

## Scale out
`docker compose -p prod -f docker-compose.yml -f docker-compose.prod.yml up -d --scale api=2`.
Caddy discovers both replicas; rate limits and cache live in Redis, so replicas share them.
