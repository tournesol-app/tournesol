#!/usr/bin/env bash

set -Eeuo pipefail

DB_DIR="db-data"

CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$CURRENT_DIR"

export DB_UID=$(id -u)
export DB_GID=$(id -g)
DOWNLOAD_PUBLIC_DATASET=false

function is_db_ready() {
  [ "$(docker inspect tournesol-dev-db --format '{{.State.Health.Status}}')" == "healthy" ]
}

function is_api_ready() {
  curl -s localhost:8000 --max-time 1 -o /dev/null
}

function is_front_ready() {
  curl -s localhost:3000 --max-time 1 -o /dev/null
}

function compose(){
  if docker compose version 2>/dev/null; then
      docker compose "$@"
  else
    if command -v docker-compose ; then
      docker-compose "$@"
    else
      echo "Please install either docker-compose or docker-compose-plugin"
      exit 1
    fi
  fi
}

function compose_up_recreate(){
  compose up --build --force-recreate -d "$@"
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
    sleep 4
  done
  echo "$service_name is unreachable."
  exit 1
}

function dev_env_restart() {
  echo "Restarting dev containers..."
  compose restart
  wait_for is_front_ready "front"
  wait_for is_api_ready "api"
  echo "You can now access Tournesol on http://localhost:3000"
}

function dev_env_recreate() {
  echo "Recreating dev containers..."
  compose_up_recreate
  wait_for is_front_ready "front"
  wait_for is_api_ready "api"
  echo "You can now access Tournesol on http://localhost:3000"
}

function dev_env_stop() {
  echo "Stopping dev containers..."
  compose stop
  echo "Docker containers are stopped."
}

function dev_env_init() {
  if [ -d $DB_DIR ]; then
    echo "The existing database at $(realpath $DB_DIR) will be deleted."
    read -p "Are you sure? (y/n) " -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]
    then
        echo "Canceled."
        exit 1
    fi
  fi

  rm -rf $DB_DIR
  mkdir -p $DB_DIR

  if [ "$DOWNLOAD_PUBLIC_DATASET" = true ] ; then
    # The database should be initialized as empty
    export DB_IMAGE="postgres:13-bullseye"
  fi

  compose_up_recreate db
  wait_for is_db_ready "db"

  compose_up_recreate
  wait_for is_api_ready "api"

  if [ "$DOWNLOAD_PUBLIC_DATASET" = true ] ; then
    docker exec tournesol-dev-api python manage.py load_public_dataset "$@"

    echo 'Creating Superuser:'
    USERNAME="user"
    PASSWORD="tournesol"
    EMAIL="superuser@example.com"
    docker exec -e DJANGO_SUPERUSER_USERNAME="$USERNAME" -e DJANGO_SUPERUSER_EMAIL="$EMAIL" -e DJANGO_SUPERUSER_PASSWORD="$PASSWORD" tournesol-dev-api python manage.py createsuperuser --no-input
  fi

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
}

function dev_env_help() {
  cat << EOF
Usage: ./run-docker-compose.sh [command]

Commands:

  init (default)
  Initialize the development environment and load the default database.
  This will ask for confirmation before deleting any existing database.
    ./run-docker-compose.sh
    ./run-docker-compose.sh init

  download
  Download up-to-date public dataset and initialize dev-env with this data.
  Options for 'load_public_dataset' management command can be passed.
  WARNING: if a Youtube API key has been configured, a large amount of queries
  to the API may be required to fetch metadata about all videos.
    ./run-docker-compose.sh download
    ./run-docker-compose.sh download --user-sampling 0.1

  restart
  Restart all dev_env services using the existing database and containers.
    ./run-docker-compose.sh restart

  recreate
  Recreate containers and restart all dev_env services using the existing database. Containers will be rebuilt if necessary.
    ./run-docker-compose.sh recreate

  stop
  Stop dev containers. The database will be persisted in "$DB_DIR" folder.
    ./run-docker-compose.sh stop
EOF
}

case ${1:-""} in
	""|init)
    dev_env_init ;;
  download)
    DOWNLOAD_PUBLIC_DATASET=true
    dev_env_init "${@:2}" ;;
  restart)
    dev_env_restart ;;
  recreate)
    dev_env_recreate ;;
  stop)
    dev_env_stop ;;
	*)
    dev_env_help ;;
esac
