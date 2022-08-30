#!/usr/bin/env bash

set -Eeuo pipefail

CURRENT_DIR="$(realpath -e "$(dirname "$0")")"

cd "$CURRENT_DIR/.."

if [[ "${1:-""}" == "apply" ]]
then
  CHECK=""
else
  CHECK="--check"
fi

if [[ "${2:-""}" == "fast" ]]
then
  echo "Using setup-fast.yaml"
  SETUP_FILE="setup-fast.yml"
else
  echo "Using setup.yaml"
  SETUP_FILE="setup.yml"
fi

GIT_REFERENCE="$(git rev-parse HEAD)"

ansible-playbook -i inventory.yml -l "$ANSIBLE_HOST" "$SETUP_FILE" \
  $CHECK \
  -e "django_database_password=$DJANGO_DATABASE_PASSWORD" \
  -e "django_secret_key=$DJANGO_SECRET_KEY" \
  -e "django_oidc_rsa_private_key=\"$(base64 <<< "$DJANGO_OIDC_RSA_PRIVATE_KEY")\"" \
  -e "django_email_host=${DJANGO_EMAIL_HOST:-""}" \
  -e "django_email_port=${DJANGO_EMAIL_PORT:-""}" \
  -e "django_email_user=${DJANGO_EMAIL_USER:-""}" \
  -e "django_email_password=${DJANGO_EMAIL_PASSWORD:-""}" \
  -e "youtube_api_key=${YOUTUBE_API_KEY:-""}" \
  -e "frontend_oauth_client_id=$FRONTEND_OAUTH_CLIENT_ID" \
  -e "frontend_oauth_client_secret=$FRONTEND_OAUTH_CLIENT_SECRET" \
  -e "grafana_admin_password=$GRAFANA_ADMIN_PASSWORD" \
  -e "mediawiki_database_password=$MEDIAWIKI_DATABASE_PASSWORD" \
  -e "mediawiki_admin_password=$MEDIAWIKI_ADMIN_PASSWORD" \
  -e "mediawiki_secret_key=$MEDIAWIKI_SECRET_KEY" \
  -e "mediawiki_oidc_client_id=$MEDIAWIKI_OIDC_CLIENT_ID" \
  -e "mediawiki_oidc_client_secret=$MEDIAWIKI_OIDC_CLIENT_SECRET" \
  -e "swagger_ui_oauth2_client_id=$SWAGGER_UI_OAUTH2_CLIENT_ID" \
  -e "swagger_ui_oauth2_client_secret=$SWAGGER_UI_OAUTH2_CLIENT_SECRET" \
  -e "grafana_oidc_client_id=$GRAFANA_OIDC_CLIENT_ID" \
  -e "grafana_oidc_client_secret=$GRAFANA_OIDC_CLIENT_SECRET" \
  -e "aws_access_key_id=${AWS_ACCESS_KEY_ID:-""}" \
  -e "aws_secret_access_key=${AWS_SECRET_ACCESS_KEY:-""}" \
  -e "git_reference=${GIT_REFERENCE}" \
  -e "consumer_key_twitterbot_fr=${TWBOT_CONSUMER_KEY_FR}" \
  -e "consumer_secret_twitterbot_fr=${TWBOT_CONSUMER_SECRET_FR}" \
  -e "access_token_twitterbot_fr=${TWBOT_ACCESS_TOKEN_FR}" \
  -e "access_token_secret_twitterbot_fr=${TWBOT_ACCESS_TOKEN_SECRET_FR}" \
  -e "consumer_key_twitterbot_en=${TWBOT_CONSUMER_KEY_EN}" \
  -e "consumer_secret_twitterbot_en=${TWBOT_CONSUMER_SECRET_EN}" \
  -e "access_token_twitterbot_en=${TWBOT_ACCESS_TOKEN_EN}" \
  -e "access_token_secret_twitterbot_en=${TWBOT_ACCESS_TOKEN_SECRET_EN}" \
  -e "discord_infra_alert_webhook=${DISCORD_INFRA_ALERT_WEBHOOK:-""}" \
  -e "discord_twitter_webhook=${DISCORD_TWITTER_WEBHOOK:-""}" \