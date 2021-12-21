#!/usr/bin/env bash

export VM_ADDR="${1:-"staging.tournesol.app"}"
export VM_USER="${2:-"$USER"}"

ssh "$VM_USER@$VM_ADDR" -- find /backups/tournesol -type d -mindepth 2 | sed 's|.*/||' | sort -nr
