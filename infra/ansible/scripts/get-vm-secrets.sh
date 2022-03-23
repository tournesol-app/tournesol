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

YOUTUBE_API_KEY="$(ssh "$VM_USER@$VM_ADDR" -- sudo cat /etc/tournesol/settings.yaml | sed -n 's/^YOUTUBE_API_KEY: \(.*\)$/\1/p')"
if [ -z "$YOUTUBE_API_KEY" ]
# For migration purposes, the YOUTUBE_API_KEY needs to be fetched temporarily from "gunicorn.service".
# To be removed after a new deployment has been applied on all environments.
then
    YOUTUBE_API_KEY="$(ssh "$VM_USER@$VM_ADDR" -- sudo cat /etc/systemd/system/gunicorn.service | sed -n 's/^Environment="YOUTUBE_API_KEY=\(.*\)"/\1/p')"
fi
export YOUTUBE_API_KEY

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

GRAFANA_OIDC_CLIENT_ID="$(ssh "$VM_USER@$VM_ADDR" -- sudo cat /root/grafana_oidc_client_id)"
export GRAFANA_OIDC_CLIENT_ID

GRAFANA_OIDC_CLIENT_SECRET="$(ssh "$VM_USER@$VM_ADDR" -- sudo cat /root/grafana_oidc_client_secret)"
export GRAFANA_OIDC_CLIENT_SECRET

DISCORD_ALERTING_WEBHOOK="$(ssh "$VM_USER@$VM_ADDR" -- sudo cat /root/discord_alerting_webhook)" && \
export DISCORD_ALERTING_WEBHOOK || \
echo "no Discord alerting webhook set"

AWS_ACCESS_KEY_ID="$(ssh "$VM_USER@$VM_ADDR" -- sudo cat /etc/systemd/system/export-backups.service | sed -n 's/^Environment="AWS_ACCESS_KEY_ID=\(.*\)"/\1/p')"
export AWS_ACCESS_KEY_ID

AWS_SECRET_ACCESS_KEY="$(ssh "$VM_USER@$VM_ADDR" -- sudo cat /etc/systemd/system/export-backups.service | sed -n 's/^Environment="AWS_SECRET_ACCESS_KEY=\(.*\)"/\1/p')"
export AWS_SECRET_ACCESS_KEY

TWBOT_CONSUMER_KEY_FR="$(ssh "$VM_USER@$VM_ADDR" -- sudo cat /etc/tournesol/settings.yaml | sed -n 's/\"CONSUMER_KEY\": \"\(.*\)\",/\1/p' | sed -n '1p')"
export TWBOT_CONSUMER_KEY_FR

TWBOT_CONSUMER_SECRET_FR="$(ssh "$VM_USER@$VM_ADDR" -- sudo cat /etc/tournesol/settings.yaml | sed -n 's/\"CONSUMER_SECRET\": \"\(.*\)\",/\1/p' | sed -n '1p')"
export TWBOT_CONSUMER_SECRET_FR

TWBOT_ACCESS_TOKEN_FR="$(ssh "$VM_USER@$VM_ADDR" -- sudo cat /etc/tournesol/settings.yaml | sed -n 's/\"ACCESS_TOKEN\": \"\(.*\)\",/\1/p' | sed -n '1p')"
export TWBOT_ACCESS_TOKEN_FR

TWBOT_ACCESS_TOKEN_SECRET_FR="$(ssh "$VM_USER@$VM_ADDR" -- sudo cat /etc/tournesol/settings.yaml | sed -n 's/\"ACCESS_TOKEN_SECRET\": \"\(.*\)\",/\1/p' | sed -n '1p')"
export TWBOT_ACCESS_TOKEN_SECRET_FR

TWBOT_CONSUMER_KEY_EN="$(ssh "$VM_USER@$VM_ADDR" -- sudo cat /etc/tournesol/settings.yaml | sed -n 's/\"CONSUMER_KEY\": \"\(.*\)\",/\1/p' | sed -n '2p')"
export TWBOT_CONSUMER_KEY_EN

TWBOT_CONSUMER_SECRET_EN="$(ssh "$VM_USER@$VM_ADDR" -- sudo cat /etc/tournesol/settings.yaml | sed -n 's/\"CONSUMER_SECRET\": \"\(.*\)\",/\1/p' | sed -n '2p')"
export TWBOT_CONSUMER_SECRET_EN

TWBOT_ACCESS_TOKEN_EN="$(ssh "$VM_USER@$VM_ADDR" -- sudo cat /etc/tournesol/settings.yaml | sed -n 's/\"ACCESS_TOKEN\": \"\(.*\)\",/\1/p' | sed -n '2p')"
export TWBOT_ACCESS_TOKEN_EN

TWBOT_ACCESS_TOKEN_SECRET_EN="$(ssh "$VM_USER@$VM_ADDR" -- sudo cat /etc/tournesol/settings.yaml | sed -n 's/\"ACCESS_TOKEN_SECRET\": \"\(.*\)\",/\1/p' | sed -n '2p')"
export TWBOT_ACCESS_TOKEN_SECRET_EN
