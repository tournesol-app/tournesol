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

ansible-playbook -i inventory.yml -l tournesol-staging setup.yml \
  $CHECK \
  -e "django_database_password=$DJANGO_DATABASE_PASSWORD" \
  -e "django_secret_key=$DJANGO_SECRET_KEY" \
  -e "django_oidc_rsa_private_key=\"$(base64 <<< "$DJANGO_OIDC_RSA_PRIVATE_KEY")\"" \
  -e "django_email_host=${DJANGO_EMAIL_HOST:-""}" \
  -e "django_email_port=${DJANGO_EMAIL_PORT:-""}" \
  -e "django_email_user=${DJANGO_EMAIL_USER:-""}" \
  -e "django_email_password=${DJANGO_EMAIL_PASSWORD:-""}" \
  -e "frontend_oauth_client_id=$FRONTEND_OAUTH_CLIENT_ID" \
  -e "frontend_oauth_client_secret=$FRONTEND_OAUTH_CLIENT_SECRET" \
  -e "grafana_admin_password=$GRAFANA_ADMIN_PASSWORD" \
  -e "mediawiki_database_password=$MEDIAWIKI_DATABASE_PASSWORD" \
  -e "mediawiki_admin_password=$MEDIAWIKI_ADMIN_PASSWORD" \
  -e "mediawiki_secret_key=$MEDIAWIKI_SECRET_KEY" \
  -e "mediawiki_oidc_client_id=$MEDIAWIKI_OIDC_CLIENT_ID" \
  -e "mediawiki_oidc_client_secret=$MEDIAWIKI_OIDC_CLIENT_SECRET" \

