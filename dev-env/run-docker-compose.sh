#!/usr/bin/env bash

set -Eeuo pipefail

DB_DIR="db-data"

CURRENT_DIR="$(realpath -e "$(dirname "$0")")"
cd "$CURRENT_DIR"

function is_db_ready() {
  [ "$(docker inspect tournesol-dev-db --format '{{.State.Health.Status}}')" == "healthy" ]
}

function is_api_ready() {
  curl -s localhost:8000 --max-time 1 -o /dev/null
}

function is_front_ready() {
  curl -s localhost:3000 --max-time 1 -o /dev/null
}

function compose_up() {
  DB_UID=$(id -u) \
  DB_GID=$(id -g) \
  docker-compose up --build --force-recreate -d "$@"
}

function wait_for() {
  local command=$1;
  local service_name=${2:-"service"}
  set +e
  for _ in $(seq 1 60); do
    if "$command"; then
      echo ""
      return 0
    fi
    echo "Waiting for $service_name to be ready..."
    sleep 3
  done
  echo "$service_name is unreachable."
  exit 1
}

if [[ "${1:-""}" == 'restart' ]]; then
  echo "Recreating dev containers..."
  compose_up
  wait_for is_front_ready "front"
  echo "You can now access Tournesol on http://localhost:3000"
  exit
fi

if [ -d $DB_DIR ]; then
  echo "The existing database at $(realpath $DB_DIR) will be deleted."
  read -p "Are you sure? (y/n) " -n 1 -r
  echo ""
  if [[ ! $REPLY =~ ^[Yy]$ ]]
  then
      echo "Canceled."
      exit 1
  fi
fi

rm -rf $DB_DIR
mkdir -p $DB_DIR

compose_up db
wait_for is_db_ready "db"

echo 'Importing dev-env dump'
tar xvf "$CURRENT_DIR"/dump-for-dev-env.sql.tgz
mv dump.sql "$CURRENT_DIR"/$DB_DIR/
docker exec --env PGPASSWORD=password tournesol-dev-db bash -c "psql -1 -q -d tournesol -U tournesol < /var/lib/postgresql/data/dump.sql"
rm "$CURRENT_DIR"/$DB_DIR/dump.sql

compose_up
wait_for is_api_ready "api"

echo 'Creating Superuser:'
USERNAME="${1:-"user"}"
PASSWORD="${2:-"tournesol"}"
EMAIL="${3:-"superuser@example.com"}"
"$CURRENT_DIR/../backend/dev-env/create-superuser.exp" "$USERNAME" "$PASSWORD" "$EMAIL"

echo 'Creating OAuth Application:'
# OAUTH_CLIENT_ID="$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 40 | head -n 1)" || true
# OAUTH_CLIENT_SECRET="$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 128 | head -n 1)" || true
OAUTH_CLIENT_ID="YlfkLzvVjmGw3gjJzdlFuMFWcR64fAk4WNg5ucGg"
OAUTH_CLIENT_SECRET="iB9j9hM5ekFpKlZQ6uNGloFJIWLVnq8LoG7SNdCtHY5oM7w9KY0XjpaDuwwJ40BshH7jKYZmXniaybhrQf5p4irAOMWv82RdYRMD6TTSJciZEAxn9onpKQoUgUeDqsRj"
now="$(date +%Y-%m-%d)"
docker exec --env PGPASSWORD=password tournesol-dev-db bash -c "psql -d tournesol -U tournesol <<< \"insert into oauth2_provider_application (client_id, redirect_uris, client_type, authorization_grant_type, client_secret, name, skip_authorization, algorithm, created, updated) values ('$OAUTH_CLIENT_ID', 'http://localhost:8000/admin/', 'confidential', 'password', '$OAUTH_CLIENT_SECRET','Frontend', true, 'RS256', '$now', '$now');\""

echo 'Creating Swagger UI OAuth Application:'
# OAUTH_CLIENT_ID="$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 40 | head -n 1)" || true
# OAUTH_CLIENT_SECRET="$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 128 | head -n 1)" || true
OAUTH_CLIENT_ID="vY17xBi0MZKZCotrfma5ympAd0hq30OudU78HZAY"
OAUTH_CLIENT_SECRET="ZJ5FZeHomIgq6uNpVgNKwJiXDfFZz1HijDhsQJlXXnFKF6R7bUqc49Dv5MNL3cYTUrE1axrTtJTSr6IkHCc417ye8bLR8facpmhD4TwQqg7ktIQ047Y2Xp0rRcKLlIvq"
now="$(date +%Y-%m-%d)"
docker exec --env PGPASSWORD=password tournesol-dev-db bash -c "psql -d tournesol -U tournesol <<< \"insert into oauth2_provider_application (client_id, redirect_uris, client_type, authorization_grant_type, client_secret, name, skip_authorization, algorithm, created, updated) values ('$OAUTH_CLIENT_ID', 'http://localhost:8000/docs/', 'confidential', 'password', '$OAUTH_CLIENT_SECRET','Swagger UI', true, 'RS256', '$now', '$now');\""

wait_for is_front_ready "front"

echo "The dev env has been created successfully!"
echo "You can now access Tournesol on http://localhost:3000"
