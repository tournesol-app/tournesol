#!/bin/bash

set -e
. ./debug_export.sh

# using file-based email backend
export EMAIL_BACKEND="file"
export DISABLE_SEARCH_YOUTUBE=1
export DJANGO_DISABLE_YOUTUBE=1
export DJANGO_DISABLE_ANALYTICS=1
export EMAIL_USE_SINGLE_THREAD=1

# generating API
./update_api.sh

# exporting javascript constants
cd backend
python manage.py js_constants --file ../frontend/src/constants.js
cd ../frontend
./node_modules/.bin/eslint src/constants.js --fix
cd ..

# disabling captcha
export DJANGO_DISABLE_RECAPTCHA=1

# testing schema generation
cd backend
# generating python API
#../frontend/node_modules/.bin/openapi-generator-cli generate -i schema.yml -g python -o python_api --package-name tournesol_api
# pip install -e tournesol_api

# removing the old database
rm db.sqlite3
# creating a new empty database
python manage.py migrate
# creating a new user
python manage.py selenium_user
# copying the clean database
cp db.sqlite3 db.sqlite3.clean

cd ..

# python linter
flake8 backend integration_test

# frontend tests
cd frontend;
npm run build
npm run test
cd ..

# backend test
cd backend
python manage.py check
# testing manage commands
python manage.py add_videos --only_download "ecqtrDTfDm4"
python manage.py add_sampled_videos
python manage.py demo_account --num_accounts 1
python manage.py set_default_features_enabled
python manage.py recompute_properties
python manage.py ml_train --epochs_override 1
python manage.py set_existing_rating_privacy --set_public False
# running tests
pytest --ignore=backend/tests/tests.py
python manage.py test
cd ..

# possibly starting Xvfb
if [ "X$DISPLAY" == "X" ]
then
        echo "Launching Xvfb..."
        export DISPLAY=:99
        screen -Sdm "xvfb_test" Xvfb $DISPLAY -screen 0 1920x1080x24
        export XDG_SESSION_TYPE=x11
	sleep 3
	if [ "X$(which x11vnc)" != "X" ]
	then
		echo "Launching x11vnc"
		screen -Sdm "xvfb_vnc" x11vnc -display $DISPLAY -loop
	fi
fi

# enabling basic auth for the API
export DJANGO_REST_ENABLE_BASIC_AUTH=1

# integration tests
echo "Starting Tournesol with basic auth..."
./launch_debug.sh

sleep 10

# creating a test user with a fixed password
selenium_user_pw=$(python backend/manage.py selenium_user)
cd integration_test
pytest 
cd ..

# resetting the database to the original status
mv backend/db.sqlite3.clean backend/db.sqlite3

# resetting the selenium user
selenium_user_pw=$(python backend/manage.py selenium_user)

# schemathesis fails if n cols is too low
stty cols 150 || true

# running API tests
schemathesis run --stateful=links --checks all http://127.0.0.1:8000/schema/ -a $selenium_user_pw --hypothesis-max-examples 10 \
    --validate-schema 1 --hypothesis-deadline 999999999 --hypothesis-suppress-health-check too_slow

# disabling basic auth for the API
unset DJANGO_REST_ENABLE_BASIC_AUTH

echo "ALL TESTS PASSED!"
