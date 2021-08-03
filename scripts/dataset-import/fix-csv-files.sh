#!/usr/bin/env bash
set -Eeuo pipefail

DIR="$(realpath -e "$(dirname "$0")")"
cd "$DIR"

# remove or fix bogus Youtube video IDs
# CtiKM0KxG-0t26s -> removed
# oAae4dGsNE0t1s -> oAae4dGsNE0
# PzI0JFof4u8t -> removed
# yNy-qLrIedMt491s -> yNy-qLrIedM

sed -i \
-e '/CtiKM0KxG-0t26s/d' \
-e '/PzI0JFof4u8t/d' \
-e 's/oAae4dGsNE0t1s/oAae4dGsNE0/g' \
-e 's/yNy-qLrIedMt491s/yNy-qLrIedM/g' \
comparison_database.csv
