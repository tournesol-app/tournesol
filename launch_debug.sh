#!/bin/bash

export DJANGO_DATABASE="sqlite"
export MODE="runserver"
export PORT=8000

. ./debug_export.sh

echo "Using database $DJANGO_DATABASE"

# https://stackoverflow.com/questions/59895/how-to-get-the-source-directory-of-a-bash-script-from-within-the-script-itself
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd $DIR

echo $DIR

function check_and_launch() {
  cmd=$1
  check=$cmd
  user=$(whoami)
  echo $cmd
  if [ "X$(ps aux -u $user|grep "$check"|grep -v grep|wc -l)" == "X0" ]
  then
    echo "Need to start $cmd as $check is not present"
    screen -S "$2" -dm $cmd
  else
    echo "Already running $cmd"
  fi
}

cd backend
check_and_launch "python manage.py shell_plus --notebook" "notebook"
check_and_launch "python manage.py runserver $PORT" "backend_server"
