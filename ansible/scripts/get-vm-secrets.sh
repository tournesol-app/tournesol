#!/usr/bin/env bash

export VM_ADDR="${1:-"staging.tournesol.app"}"
export VM_USER="${2:-"$USER"}"

DJANGO_SECRET_KEY="$(ssh "$VM_USER@$VM_ADDR" -- sudo cat /etc/tournesol/settings.yaml | sed -n 's/^SECRET_KEY: \(.*\)$/\1/p')"
export DJANGO_SECRET_KEY

DJANGO_DATABASE_PASSWORD="$(ssh "$VM_USER@$VM_ADDR" -- sudo cat /etc/tournesol/settings.yaml | sed -n 's/^DATABASE_PASSWORD: \(.*\)$/\1/p')"
export DJANGO_DATABASE_PASSWORD

DJANGO_EMAIL_HOST="$(ssh "$VM_USER@$VM_ADDR" -- sudo cat /etc/tournesol/settings.yaml | sed -n 's/^EMAIL_HOST: \(.*\)$/\1/p')"
export DJANGO_EMAIL_HOST

DJANGO_EMAIL_PORT="$(ssh "$VM_USER@$VM_ADDR" -- sudo cat /etc/tournesol/settings.yaml | sed -n 's/^EMAIL_PORT: \(.*\)$/\1/p')"
export DJANGO_EMAIL_PORT

DJANGO_EMAIL_USER="$(ssh "$VM_USER@$VM_ADDR" -- sudo cat /etc/tournesol/settings.yaml | sed -n 's/^EMAIL_HOST_USER: \(.*\)$/\1/p')"
export DJANGO_EMAIL_USER

DJANGO_EMAIL_PASSWORD="$(ssh "$VM_USER@$VM_ADDR" -- sudo cat /etc/tournesol/settings.yaml | sed -n 's/^EMAIL_HOST_PASSWORD: \(.*\)$/\1/p')"
export DJANGO_EMAIL_PASSWORD

DJANGO_OIDC_RSA_PRIVATE_KEY="$(ssh "$VM_USER@$VM_ADDR" -- sudo cat /root/django_oidc_rsa_private_key)"
export DJANGO_OIDC_RSA_PRIVATE_KEY

FRONTEND_OAUTH_CLIENT_ID="$(ssh "$VM_USER@$VM_ADDR" -- sudo cat /root/frontend_oauth_client_id)"
export FRONTEND_OAUTH_CLIENT_ID

FRONTEND_OAUTH_CLIENT_SECRET="$(ssh "$VM_USER@$VM_ADDR" -- sudo cat /root/frontend_oauth_client_secret)"
export FRONTEND_OAUTH_CLIENT_SECRET

GRAFANA_ADMIN_PASSWORD="$(ssh "$VM_USER@$VM_ADDR" -- sudo cat /root/grafana_admin_password)"
export GRAFANA_ADMIN_PASSWORD

MEDIAWIKI_DATABASE_PASSWORD="$(ssh "$VM_USER@$VM_ADDR" -- sudo cat /root/mediawiki_database_password)"
export MEDIAWIKI_DATABASE_PASSWORD

MEDIAWIKI_ADMIN_PASSWORD="$(ssh "$VM_USER@$VM_ADDR" -- sudo cat /root/mediawiki_admin_password)"
export MEDIAWIKI_ADMIN_PASSWORD

MEDIAWIKI_SECRET_KEY="$(ssh "$VM_USER@$VM_ADDR" -- sudo cat /root/mediawiki_secret_key)"
export MEDIAWIKI_SECRET_KEY

MEDIAWIKI_OIDC_CLIENT_ID="$(ssh "$VM_USER@$VM_ADDR" -- sudo cat /root/mediawiki_oidc_client_id)"
export MEDIAWIKI_OIDC_CLIENT_ID

MEDIAWIKI_OIDC_CLIENT_SECRET="$(ssh "$VM_USER@$VM_ADDR" -- sudo cat /root/mediawiki_oidc_client_secret)"
export MEDIAWIKI_OIDC_CLIENT_SECRET

SWAGGER_UI_OAUTH2_CLIENT_ID="$(ssh "$VM_USER@$VM_ADDR" -- sudo cat /root/swagger_ui_oauth2_client_id)"
export SWAGGER_UI_OAUTH2_CLIENT_ID

SWAGGER_UI_OAUTH2_CLIENT_SECRET="$(ssh "$VM_USER@$VM_ADDR" -- sudo cat /root/swagger_ui_oauth2_client_secret)"
export SWAGGER_UI_OAUTH2_CLIENT_SECRET

DISCORD_ALERTING_WEBHOOK="$(ssh "$VM_USER@$VM_ADDR" -- sudo cat /root/discord_alerting_webhook)" && \
export DISCORD_ALERTING_WEBHOOK || \
echo "no Discord alerting webhook set"
