#!/bin/bash


echo "Using DEBUG environment"

export DJANGO_DATABASE="sqlite"
export DJANGO_DISABLE_ANALYTICS=1
export SECRET_KEY="b!dmu^_-n^4dvtn!r)r!0gzh@pa-5nqaxu%b@(pl-lkq5jhnc4"
export POSTGRES_DB_PASSWORD="unknown"
export SOCIAL_AUTH_GOOGLE_OAUTH2_KEY="get_yours_from_google_cloud.com"
export SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET="unknown"
export DRF_RECAPTCHA_PUBLIC_KEY="get_yours_from_recaptcha"
export DRF_RECAPTCHA_SECRET_KEY="unknown"
export COMMENT_USERNAME_SALT="tournesol_salt_dae7oDe0aongie9"

