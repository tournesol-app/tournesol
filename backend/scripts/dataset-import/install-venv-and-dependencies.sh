#!/usr/bin/env bash
set -Eeuo pipefail

DIR="$(realpath -e "$(dirname "$0")")"
cd "$DIR"

sudo curl -L https://yt-dl.org/downloads/latest/youtube-dl -o /usr/local/bin/youtube-dl
sudo chmod a+rx /usr/local/bin/youtube-dl

sudo apt update
sudo apt -y install python3-venv python3-dev libpq-dev pkg-config libicu-dev jq sqlite3

if [[ ! -d venv-import-dataset ]]
then
    python3.9 -m venv venv-import-dataset
fi
source venv-import-dataset/bin/activate
pip install -U pip
pip install csvkit
pip install psycopg2
