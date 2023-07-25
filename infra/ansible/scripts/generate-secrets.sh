#!/usr/bin/env bash

DJANGO_SECRET_KEY="$(base64 /dev/urandom | head -c 32)"
export DJANGO_SECRET_KEY

DJANGO_DATABASE_PASSWORD="$(base64 /dev/urandom | head -c 32)"
export DJANGO_DATABASE_PASSWORD

DJANGO_OIDC_RSA_PRIVATE_KEY="$(openssl genrsa 4096)"
export DJANGO_OIDC_RSA_PRIVATE_KEY

FRONTEND_OAUTH_CLIENT_ID="$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 40 | head -n 1)"
export FRONTEND_OAUTH_CLIENT_ID

FRONTEND_OAUTH_CLIENT_SECRET="$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 128 | head -n 1)"
export FRONTEND_OAUTH_CLIENT_SECRET

GRAFANA_ADMIN_PASSWORD="$(base64 /dev/urandom | head -c 32)"
export GRAFANA_ADMIN_PASSWORD

SWAGGER_UI_OAUTH2_CLIENT_ID="$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 40 | head -n 1)"
export SWAGGER_UI_OAUTH2_CLIENT_ID

SWAGGER_UI_OAUTH2_CLIENT_SECRET="$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 128 | head -n 1)"
export SWAGGER_UI_OAUTH2_CLIENT_SECRET

GRAFANA_OIDC_CLIENT_ID="$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 40 | head -n 1)"
export GRAFANA_OIDC_CLIENT_ID

GRAFANA_OIDC_CLIENT_SECRET="$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 128 | head -n 1)"
export GRAFANA_OIDC_CLIENT_SECRET

PLAUSIBLE_ANALYTICS_SECRET_KEY="$(openssl rand -base64 64 | tr -d '\n' ; echo | head -n 1)"
export PLAUSIBLE_ANALYTICS_SECRET_KEY
