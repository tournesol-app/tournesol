#!/usr/bin/env bash
set -Eeuo pipefail

DIR="$(realpath -e "$(dirname "$0")")"
cd "$DIR"

now="$(date -I)"

source venv-import-dataset/bin/activate

csvcut -c 1,3,4,5,6,12,8,13,7,9,10,11 contributors_public.csv > tmp1-contributors.csv

sed -i 's/user__username/username/' tmp1-contributors.csv

echo 'date_joined,is_superuser,is_staff,is_active,is_demo,comment_anonymously,show_online_presence,show_my_profile,password,email,gender,nationality,residence,race,political_affiliation,religion,degree_of_political_engagement,moral_philosophy' | csvjoin - tmp1-contributors.csv > tmp2-contributors.csv
rm tmp1-contributors.csv

sed '2,$s/^,,,,,,,,,,,,,,,,,,/'"$now"',false,false,true,false,false,true,true,xxx,xxx@xxx.xxx,Not Specified,Not Specified,Not Specified,Not Specified,Not Specified,Not Specified,Not Specified,Not Specified,/' tmp2-contributors.csv > core_user.csv
rm tmp2-contributors.csv

sudo -u postgres bash -c "source venv-import-dataset/bin/activate && csvsql --db postgresql+psycopg2:///tournesol --no-create --insert core_user.csv"
rm core_user.csv
