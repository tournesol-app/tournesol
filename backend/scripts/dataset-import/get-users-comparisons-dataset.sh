#!/usr/bin/env bash
set -Eeuo pipefail

DIR="$(realpath -e "$(dirname "$0")")"
cd "$DIR"

source venv-import-dataset/bin/activate

csvcut -c 25 comparison_database.csv | sed '1d' > tmp1-users.csv
sort tmp1-users.csv | uniq > tmp2-users.csv
rm tmp1-users.csv
echo "username" > tmp3-users.csv
cat tmp2-users.csv >> tmp3-users.csv
rm tmp2-users.csv
echo "user_id" > tmp4-users.csv
sed '1d' tmp3-users.csv | while read -r user
do
    user="${user//\'/\'\'}"
    rows=$(sudo -u postgres psql -t --csv -d tournesol <<< "select id from core_user where username = '$user';")
    echo "$rows" >> tmp4-users.csv
done

csvjoin tmp3-users.csv tmp4-users.csv > tmp5-users.csv
rm tmp3-users.csv tmp4-users.csv

# spotted-lion-8lvEKg doesn't exists in DB
sed '/^spotted-lion-8lvEKg/d' tmp5-users.csv > tmp6-users.csv
rm tmp5-users.csv
