#!/usr/bin/env bash

DJANGO_SECRET_KEY="$(ssh tournesol.technocracy.dev -- sudo cat /etc/tournesol/settings.yaml | sed -n 's/^SECRET_KEY: \(.*\)$/\1/p')"
export DJANGO_SECRET_KEY

DJANGO_DATABASE_PASSWORD="$(ssh tournesol.technocracy.dev -- sudo cat /etc/tournesol/settings.yaml | sed -n 's/^DATABASE_PASSWORD: \(.*\)$/\1/p')"
export DJANGO_DATABASE_PASSWORD
