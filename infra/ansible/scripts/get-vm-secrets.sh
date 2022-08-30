#!/usr/bin/env bash

export VM_ADDR="${1:-"staging.tournesol.app"}"
export VM_USER="${2:-"$USER"}"

function get_settings_value() {
    local jq_filter=$1;
    ssh "$VM_USER@$VM_ADDR" -- \
    'python3 -c '\''import yaml,json; print(json.dumps(yaml.safe_load(open("/etc/tournesol/settings.yaml"))))'\'' \
    | jq -r' "'$jq_filter | values'"
}

DJANGO_SECRET_KEY=$(get_settings_value .SECRET_KEY)
export DJANGO_SECRET_KEY

DJANGO_DATABASE_PASSWORD=$(get_settings_value .DATABASE_PASSWORD)
export DJANGO_DATABASE_PASSWORD

DJANGO_EMAIL_HOST=$(get_settings_value .EMAIL_HOST)
export DJANGO_EMAIL_HOST

DJANGO_EMAIL_PORT=$(get_settings_value .EMAIL_PORT)
export DJANGO_EMAIL_PORT

DJANGO_EMAIL_USER=$(get_settings_value .EMAIL_HOST_USER)
export DJANGO_EMAIL_USER

DJANGO_EMAIL_PASSWORD=$(get_settings_value .EMAIL_HOST_PASSWORD)
export DJANGO_EMAIL_PASSWORD

DJANGO_OIDC_RSA_PRIVATE_KEY="$(ssh "$VM_USER@$VM_ADDR" -- sudo cat /root/django_oidc_rsa_private_key)"
export DJANGO_OIDC_RSA_PRIVATE_KEY

YOUTUBE_API_KEY=$(get_settings_value .YOUTUBE_API_KEY)
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

AWS_ACCESS_KEY_ID="$(ssh "$VM_USER@$VM_ADDR" -- sudo cat /etc/systemd/system/export-backups.service | sed -n 's/^Environment="AWS_ACCESS_KEY_ID=\(.*\)"/\1/p')"
export AWS_ACCESS_KEY_ID

AWS_SECRET_ACCESS_KEY="$(ssh "$VM_USER@$VM_ADDR" -- sudo cat /etc/systemd/system/export-backups.service | sed -n 's/^Environment="AWS_SECRET_ACCESS_KEY=\(.*\)"/\1/p')"
export AWS_SECRET_ACCESS_KEY

TWBOT_CONSUMER_KEY_FR=$(get_settings_value .TWITTERBOT_CREDENTIALS.\"@TournesolBotFR\".CONSUMER_KEY)
export TWBOT_CONSUMER_KEY_FR

TWBOT_CONSUMER_SECRET_FR=$(get_settings_value .TWITTERBOT_CREDENTIALS.\"@TournesolBotFR\".CONSUMER_SECRET)
export TWBOT_CONSUMER_SECRET_FR

TWBOT_ACCESS_TOKEN_FR=$(get_settings_value .TWITTERBOT_CREDENTIALS.\"@TournesolBotFR\".ACCESS_TOKEN)
export TWBOT_ACCESS_TOKEN_FR

TWBOT_ACCESS_TOKEN_SECRET_FR=$(get_settings_value .TWITTERBOT_CREDENTIALS.\"@TournesolBotFR\".ACCESS_TOKEN_SECRET)
export TWBOT_ACCESS_TOKEN_SECRET_FR

TWBOT_CONSUMER_KEY_EN=$(get_settings_value .TWITTERBOT_CREDENTIALS.\"@TournesolBot\".CONSUMER_KEY)
export TWBOT_CONSUMER_KEY_EN

TWBOT_CONSUMER_SECRET_EN=$(get_settings_value .TWITTERBOT_CREDENTIALS.\"@TournesolBot\".CONSUMER_SECRET)
export TWBOT_CONSUMER_SECRET_EN

TWBOT_ACCESS_TOKEN_EN=$(get_settings_value .TWITTERBOT_CREDENTIALS.\"@TournesolBot\".ACCESS_TOKEN)
export TWBOT_ACCESS_TOKEN_EN

TWBOT_ACCESS_TOKEN_SECRET_EN=$(get_settings_value .TWITTERBOT_CREDENTIALS.\"@TournesolBot\".ACCESS_TOKEN_SECRET)
export TWBOT_ACCESS_TOKEN_SECRET_EN

DISCORD_INFRA_ALERT_WEBHOOK=$(get_settings_value .DISCORD_CHANNEL_WEBHOOKS.infra_alert)
export DISCORD_INFRA_ALERT_WEBHOOK

DISCORD_TWITTER_WEBHOOK=$(get_settings_value .DISCORD_CHANNEL_WEBHOOKS.twitter)
export DISCORD_TWITTER_WEBHOOK
