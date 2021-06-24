#!/usr/bin/env bash

export VM_ADDR="${1:-"staging.tournesol.app"}"
export VM_USER="${2:-"$USER"}"

DJANGO_SECRET_KEY="$(ssh "$VM_USER@$VM_ADDR" -- sudo cat /etc/tournesol/settings.yaml | sed -n 's/^SECRET_KEY: \(.*\)$/\1/p')"
export DJANGO_SECRET_KEY

DJANGO_DATABASE_PASSWORD="$(ssh "$VM_USER@$VM_ADDR" -- sudo cat /etc/tournesol/settings.yaml | sed -n 's/^DATABASE_PASSWORD: \(.*\)$/\1/p')"
export DJANGO_DATABASE_PASSWORD

GRAFANA_ADMIN_PASSWORD="$(ssh "$VM_USER@$VM_ADDR" -- sudo cat /root/grafana_admin_password)"
export GRAFANA_ADMIN_PASSWORD

MEDIAWIKI_DATABASE_PASSWORD="$(ssh "$VM_USER@$VM_ADDR" -- sudo cat /root/mediawiki_database_password)"
export MEDIAWIKI_DATABASE_PASSWORD

MEDIAWIKI_ADMIN_PASSWORD="$(ssh "$VM_USER@$VM_ADDR" -- sudo cat /root/mediawiki_admin_password)"
export MEDIAWIKI_ADMIN_PASSWORD

MEDIAWIKI_SECRET_KEY="$(ssh "$VM_USER@$VM_ADDR" -- sudo cat /root/mediawiki_secret_key)"
export MEDIAWIKI_SECRET_KEY
