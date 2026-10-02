#!/usr/bin/env bash
# One-time, idempotent setup of an ExpenseFlow production server (Ubuntu 24.04). Safe to run again: every step
# checks before it acts, and an existing .env or SSH key is never overwritten.
#
#   curl -fsSL https://raw.githubusercontent.com/RrezeKonjusha/expenseflow/main/scripts/server-bootstrap.sh \
#     | sudo bash -s -- --domain expenseflow.example.com
#
# Options:
#   --domain NAME      public domain whose A record points at this server (required)
#   --email-url URL    outgoing mail, e.g. submission://USER:PASS@smtp-relay.brevo.com:587 (default: console://,
#                      emails are printed to the API log until you set a real one)
#   --repo URL         git repository (default: https://github.com/RrezeKonjusha/expenseflow.git)
#   --branch NAME      branch the server follows (default: main)
#
# What it does: Docker Engine + Compose plugin, Docker log rotation, 2 GB swap, firewall (22, 80, 443), a `deploy`
# user in the docker group with an SSH key for GitHub Actions, the repository in ~deploy/expenseflow-prod, a .env
# with generated secrets, and the nightly backup cron. It does not start the stack: the first deploy comes from
# GitHub Actions, which builds and pushes the images.
set -euo pipefail

DOMAIN="" EMAIL_URL="console://" REPO="https://github.com/RrezeKonjusha/expenseflow.git" BRANCH="main"
while [ $# -gt 0 ]; do
  case "$1" in
    --domain) DOMAIN=$2; shift 2 ;;
    --email-url) EMAIL_URL=$2; shift 2 ;;
    --repo) REPO=$2; shift 2 ;;
    --branch) BRANCH=$2; shift 2 ;;
    *) echo "unknown option $1" >&2; exit 2 ;;
  esac
done
[ -n "$DOMAIN" ] || { echo "usage: server-bootstrap.sh --domain your.domain [--email-url URL]" >&2; exit 2; }
[ "$(id -u)" -eq 0 ] || { echo "run as root (sudo)" >&2; exit 2; }

USER_NAME=deploy
HOME_DIR=/home/$USER_NAME
APP_DIR=$HOME_DIR/expenseflow-prod
REGISTRY="ghcr.io/$(basename "$(dirname "$REPO")" | tr '[:upper:]' '[:lower:]')/expenseflow"
step() { printf '\n== %s\n' "$1"; }

step "System packages"
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq ca-certificates curl git ufw openssl cron >/dev/null

step "Docker Engine and Compose plugin"
if docker compose version >/dev/null 2>&1; then
  echo "already installed: $(docker --version)"
else
  install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
  chmod a+r /etc/apt/keyrings/docker.asc
  . /etc/os-release
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu ${VERSION_CODENAME} stable" \
    > /etc/apt/sources.list.d/docker.list
  apt-get update -qq
  apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin >/dev/null
  echo "installed: $(docker --version)"
fi
if [ ! -f /etc/docker/daemon.json ]; then
  # container logs would otherwise grow until the disk is full
  install -d /etc/docker
  echo '{"log-driver": "json-file", "log-opts": {"max-size": "10m", "max-file": "3"}}' > /etc/docker/daemon.json
  systemctl restart docker
  echo "log rotation configured"
fi
systemctl enable --now docker >/dev/null

step "Swap (2 GB)"
if swapon --show | grep -q .; then
  echo "swap already active"
else
  fallocate -l 2G /swapfile && chmod 600 /swapfile && mkswap /swapfile >/dev/null && swapon /swapfile
  grep -q '^/swapfile' /etc/fstab || echo '/swapfile none swap sw 0 0' >> /etc/fstab
  echo "swap on"
fi

step "Firewall: SSH, HTTP, HTTPS only"
ufw allow OpenSSH >/dev/null
ufw allow 80/tcp >/dev/null
ufw allow 443/tcp >/dev/null
ufw allow 443/udp >/dev/null # HTTP/3
ufw --force enable >/dev/null
ufw status | sed -n '1,12p'

step "Deploy user"
if id "$USER_NAME" >/dev/null 2>&1; then
  echo "user $USER_NAME exists"
else
  adduser --disabled-password --gecos "" "$USER_NAME" >/dev/null
  echo "user $USER_NAME created"
fi
getent group docker >/dev/null || groupadd docker
usermod -aG docker "$USER_NAME"
install -d -m 700 -o "$USER_NAME" -g "$USER_NAME" "$HOME_DIR/.ssh" "$HOME_DIR/backups"
KEY=$HOME_DIR/.ssh/github_actions_ed25519
if [ ! -f "$KEY" ]; then
  sudo -u "$USER_NAME" ssh-keygen -q -t ed25519 -N "" -C "github-actions-deploy" -f "$KEY"
  echo "deploy key generated"
fi
touch "$HOME_DIR/.ssh/authorized_keys"
grep -qF "$(cat "$KEY.pub")" "$HOME_DIR/.ssh/authorized_keys" || cat "$KEY.pub" >> "$HOME_DIR/.ssh/authorized_keys"
chown "$USER_NAME:$USER_NAME" "$HOME_DIR/.ssh/authorized_keys" && chmod 600 "$HOME_DIR/.ssh/authorized_keys"

step "Repository"
if [ -d "$APP_DIR/.git" ]; then
  sudo -u "$USER_NAME" git -C "$APP_DIR" pull -q --ff-only
  echo "updated $APP_DIR"
else
  sudo -u "$USER_NAME" git clone -q -b "$BRANCH" "$REPO" "$APP_DIR"
  echo "cloned into $APP_DIR"
fi

step "Environment file (.env)"
ENV=$APP_DIR/.env
if [ -f "$ENV" ]; then
  echo ".env exists, left unchanged"
else
  secret() { openssl rand -hex "$1"; }
  PG_PASS=$(secret 24)
  sed -e "s|^SITE_DOMAIN=.*|SITE_DOMAIN=$DOMAIN|" \
      -e "s|^FRONTEND_URL=.*|FRONTEND_URL=https://$DOMAIN|" \
      -e "s|^ALLOWED_HOSTS=.*|ALLOWED_HOSTS=$DOMAIN,api|" \
      -e "s|^CSRF_TRUSTED_ORIGINS=.*|CSRF_TRUSTED_ORIGINS=https://$DOMAIN|" \
      -e "s|^CORS_ALLOWED_ORIGINS=.*|CORS_ALLOWED_ORIGINS=https://$DOMAIN|" \
      -e "s|^DJANGO_SECRET_KEY=.*|DJANGO_SECRET_KEY=$(secret 48)|" \
      -e "s|^JWT_SIGNING_KEY=.*|JWT_SIGNING_KEY=$(secret 48)|" \
      -e "s|^DJANGO_DEBUG=.*|DJANGO_DEBUG=0|" \
      -e "s|^POSTGRES_PASSWORD=.*|POSTGRES_PASSWORD=$PG_PASS|" \
      -e "s|^DATABASE_URL=.*|DATABASE_URL=postgres://expenseflow:$PG_PASS@postgres:5432/expenseflow|" \
      -e "s|^EMAIL_URL=.*|EMAIL_URL=$EMAIL_URL|" \
      -e "s|^DEFAULT_FROM_EMAIL=.*|DEFAULT_FROM_EMAIL=ExpenseFlow <no-reply@$DOMAIN>|" \
      -e "s|^GRAFANA_PASSWORD=.*|GRAFANA_PASSWORD=$(secret 12)|" \
      -e "s|^REGISTRY=.*|REGISTRY=$REGISTRY|" \
      "$APP_DIR/.env.example" > "$ENV"
  chown "$USER_NAME:$USER_NAME" "$ENV" && chmod 600 "$ENV"
  echo ".env written with generated secrets (chmod 600)"
fi

step "Nightly backup at 02:00"
CRON="0 2 * * * cd $APP_DIR && scripts/backup.sh >> $HOME_DIR/backups/backup.log 2>&1"
{ crontab -u "$USER_NAME" -l 2>/dev/null | grep -vF "scripts/backup.sh" || true; echo "$CRON"; } | crontab -u "$USER_NAME" -
crontab -u "$USER_NAME" -l | grep backup

IP=$(curl -fsS -4 https://api.ipify.org || hostname -I | awk '{print $1}')
cat <<EOF

== Done. Add these in GitHub: Settings > Environments > production > Environment secrets

  VPS_HOST     $IP
  VPS_USER     $USER_NAME
  DOMAIN       $DOMAIN
  VPS_SSH_KEY  (the whole private key below, including the BEGIN and END lines)

$(cat "$KEY")

Then run the first deploy: GitHub > Actions > Deploy > Run workflow (branch main).
Grafana: https://$DOMAIN/grafana/  user admin, password: grep GRAFANA_PASSWORD $ENV
EOF
