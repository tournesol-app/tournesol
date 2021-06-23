#!/usr/bin/env bash

DJANGO_SECRET_KEY="$(base64 /dev/urandom | head -c 32)"
export DJANGO_SECRET_KEY

DJANGO_DATABASE_PASSWORD="$(base64 /dev/urandom | head -c 32)"
export DJANGO_DATABASE_PASSWORD

GRAFANA_ADMIN_PASSWORD="$(base64 /dev/urandom | head -c 32)"
export GRAFANA_ADMIN_PASSWORD

MEDIAWIKI_DATABASE_PASSWORD="$(base64 /dev/urandom | head -c 32)"
export MEDIAWIKI_DATABASE_PASSWORD

MEDIAWIKI_ADMIN_PASSWORD="$(base64 /dev/urandom | head -c 32)"
export MEDIAWIKI_ADMIN_PASSWORD

MEDIAWIKI_SECRET_KEY="$(openssl rand -hex 32)"
export MEDIAWIKI_SECRET_KEY
