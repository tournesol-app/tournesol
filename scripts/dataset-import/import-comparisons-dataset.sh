#!/usr/bin/env bash
set -Eeuo pipefail

DIR="$(realpath -e "$(dirname "$0")")"
cd "$DIR"

source venv-import-dataset/bin/activate

csvcut -c 1,2,3,4,12,22,13,23,11,21,8,18,14,24,7,17,5,15,10,20,9,19,6,16,26,27,25 comparison_database.csv > tmp1-comparisons.csv

sed -i '1s/user__user__username/username/' tmp1-comparisons.csv
csvjoin -c username tmp1-comparisons.csv tmp6-users.csv > tmp2-comparisons.csv
rm tmp1-comparisons.csv tmp6-users.csv

sed '1s/,id$/,video_1_id/' tmp12-videos.csv > tmp13-videos.csv
sed '1s/,id$/,video_2_id/' tmp12-videos.csv > tmp14-videos.csv
csvjoin -c video_1__video_id,video_id tmp2-comparisons.csv tmp13-videos.csv > tmp3-comparisons.csv
csvjoin -c video_2__video_id,video_id tmp3-comparisons.csv tmp14-videos.csv > tmp4-comparisons.csv
rm tmp2-comparisons.csv tmp3-comparisons.csv tmp12-videos.csv tmp13-videos.csv tmp14-videos.csv

echo 'video_1_2_ids_sorted' > tmp5-comparisons.csv
sed '1d' tmp4-comparisons.csv | awk '
    BEGIN{FS=","}
    {if($25<$26) {print $25 "_" $26} else {print $26 "_" $25}}
' >> tmp5-comparisons.csv

csvjoin tmp4-comparisons.csv tmp5-comparisons.csv > tmp6-comparisons.csv
rm tmp4-comparisons.csv tmp5-comparisons.csv

csvcut -C 25,26,27 tmp6-comparisons.csv > tournesol_comparison.csv
rm tmp6-comparisons.csv

csvsql --db sqlite:////tmp/tournesol.db --no-create --before-insert '
CREATE TABLE tournesol_comparison (
	id INTEGER NOT NULL, 
	duration_ms FLOAT NOT NULL, 
	datetime_lastedit VARCHAR NOT NULL, 
	datetime_add VARCHAR NOT NULL, 
	backfire_risk FLOAT, 
	backfire_risk_weight FLOAT NOT NULL, 
	better_habits FLOAT, 
	better_habits_weight FLOAT NOT NULL, 
	diversity_inclusion FLOAT, 
	diversity_inclusion_weight FLOAT NOT NULL, 
	engaging FLOAT, 
	engaging_weight FLOAT NOT NULL, 
	entertaining_relaxing FLOAT, 
	entertaining_relaxing_weight FLOAT NOT NULL, 
	importance FLOAT, 
	importance_weight FLOAT NOT NULL, 
	largely_recommended FLOAT, 
	largely_recommended_weight FLOAT NOT NULL, 
	layman_friendly FLOAT, 
	layman_friendly_weight FLOAT NOT NULL, 
	pedagogy FLOAT, 
	pedagogy_weight FLOAT NOT NULL, 
	reliability FLOAT, 
	reliability_weight FLOAT NOT NULL, 
	user_id FLOAT NOT NULL, 
	video_1_id INTEGER NOT NULL, 
	video_2_id INTEGER NOT NULL, 
	video_1_2_ids_sorted VARCHAR NOT NULL
);
' --insert tournesol_comparison.csv
sqlite3 /tmp/tournesol.db <<< "delete from tournesol_comparison as r1 where r1.datetime_lastedit < (select max(r2.datetime_lastedit) from tournesol_comparison as r2 where r1.id = r2.id);"
sql2csv --db sqlite:////tmp/tournesol.db --query "select * from tournesol_comparison;" | uniq > tournesol_comparison.csv
rm /tmp/tournesol.db

sudo -u postgres bash -c "source venv-import-dataset/bin/activate && csvsql --db postgresql+psycopg2:///tournesol --no-create --insert tournesol_comparison.csv"
rm tournesol_comparison.csv
