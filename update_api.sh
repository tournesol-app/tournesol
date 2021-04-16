#!/bin/bash

set -e

# testing schema generation
cd backend
python manage.py spectacular --file schema.yml --validate --lang en
python manage.py spectacular --file schema.json --format openapi-json --validate --lang en
apistar validate --path schema.json --format openapi
# generating docs
../frontend/node_modules/.bin/openapi-generator-cli generate -i schema.yml -g markdown -o ../API
cd ..
cd frontend
# generating API
./node_modules/.bin/openapi-generator-cli generate -i ../backend/schema.json -g javascript -o api
cd ..


# testing documentation creation
#cd backend/doc
#sphinx-apidoc -f -o source ..
#make html
#cd ../..
