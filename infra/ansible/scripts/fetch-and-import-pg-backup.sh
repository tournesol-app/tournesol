#!/usr/bin/env bash

set -Eeuo pipefail

CURRENT_DIR="$(realpath -e "$(dirname "$0")")"
cd "$CURRENT_DIR/.."

function usage(){
    printf "Usage:\n\t%s\n" "${0} --backup-name 2021-11-12-weekly --from staging.tournesol.app --to-ansible-host tournesol-vm"
}

if test "$#" -lt 6; then
    usage
    exit 1
fi

declare -A ansible_host_to_domain_name=(
    ["tournesol-vm"]="tournesol-vm"
    ["tournesol-staging"]="staging.tournesol.app"
    ["tournesol-prod"]="tournesol.app"
)

set +u
while test -n "$1"; do
    case "$1" in
      -b|--backup-name)
          BACKUP_NAME=$2
          shift 2
          ;;
      -f|--from)
          FROM_DOMAIN_NAME=$2
          shift 2
          ;;
      -t|--to-ansible-host)
          ANSIBLE_HOST=$2
          TO_DOMAIN_NAME=${ansible_host_to_domain_name[$ANSIBLE_HOST]}
          if ! test -n "$TO_DOMAIN_NAME"; then
            echo "Unknown ansible host '$ANSIBLE_HOST'"
            exit 1
          fi
          shift 2
          ;;
    esac
done
set -u

function copy_backup() {
    ssh "$TO_DOMAIN_NAME" -- sudo -u postgres mkdir -m 777 -p /backups/tournesol/"$FROM_DOMAIN_NAME"
    scp -C -3 -r "$FROM_DOMAIN_NAME":/backups/tournesol/db/"$BACKUP_NAME" "$TO_DOMAIN_NAME":/backups/tournesol/"$FROM_DOMAIN_NAME"/"$BACKUP_NAME" 
}

if ! copy_backup; then
  echo "Failed to copy backup from '$FROM_DOMAIN_NAME' to '$TO_DOMAIN_NAME'".
  exit 1;
fi

ansible-playbook -i inventory.yml -l "$ANSIBLE_HOST" restore-backup.yml \
    -e external_backup_path=/backups/tournesol/"$FROM_DOMAIN_NAME"/"$BACKUP_NAME"
