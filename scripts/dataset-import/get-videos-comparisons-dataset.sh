#!/usr/bin/env bash
set -Eeuo pipefail

DIR="$(dirname "$0")"
cd "$DIR"

source venv-import-dataset/bin/activate

csvcut -c 26 comparison_database.csv | sed '1d' > tmp1-videos.csv
csvcut -c 27 comparison_database.csv | sed '1d' >> tmp1-videos.csv
sort tmp1-videos.csv | uniq > tmp2-videos.csv
rm tmp1-videos.csv
echo "video_id" > tmp3-videos.csv
cat tmp2-videos.csv >> tmp3-videos.csv
rm tmp2-videos.csv

# some video IDs lack a - in front (i.e. DfX3_CO2bU, F0Ygj2pCpg should be -DfX3_CO2bU, -F0Ygj2pCpg)
# some lack something else (i.e. jSWFkGY6O should probably be jSWFkGY6O-0)
# these are buggy too...
# httpswwwyoutubecompl,
# httpswwwyoutubecomre,
# httpswwwyoutubecomwa,
# httpsyoutubeLZGhBmDV,
sed -i -e '/^DfX3_CO2bU/d' -e '/^F0Ygj2pCpg/d' -e '/^jSWFkGY6O$/d' -e '/^httpswwwyoutube/d' -e '/^httpsyoutube/d' tmp3-videos.csv

echo 'name,wrong_url,is_unlisted,download_attempts,download_failed,is_update_pending,pareto_optimal,rating_n_contributors,rating_n_ratings,n_public_contributors,n_private_contributors,public_contributors,backfire_risk,backfire_risk_quantile,backfire_risk_uncertainty,better_habits,better_habits_quantile,better_habits_uncertainty,diversity_inclusion,diversity_inclusion_quantile,diversity_inclusion_uncertainty,engaging,engaging_quantile,engaging_uncertainty,entertaining_relaxing,entertaining_relaxing_quantile,entertaining_relaxing_uncertainty,importance,importance_quantile,importance_uncertainty,largely_recommended,largely_recommended_quantile,largely_recommended_uncertainty,layman_friendly,layman_friendly_quantile,layman_friendly_uncertainty,pedagogy,pedagogy_quantile,pedagogy_uncertainty,reliability,reliability_quantile,reliability_uncertainty' > tmp8-videos.csv
csvjoin tmp8-videos.csv tmp3-videos.csv > tmp9-videos.csv
sed '2,$s/^,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,/"Not Specified",false,false,0,false,false,false,0,0,0,0,"{}",0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,/' tmp9-videos.csv > tournesol_video.csv

sudo -u postgres bash -c "source venv-import-dataset/bin/activate && csvsql --no-inference --db postgresql+psycopg2:///tournesol --no-create --insert tournesol_video.csv"
rm tournesol_video.csv


echo "id" > tmp11-videos.csv
sed '1d' tmp3-videos.csv | while read -r vid
do
    echo "$vid"
    rows=$(sudo -u postgres psql -t --csv -d tournesol <<< "select id from tournesol_video where video_id = '$vid';")
    echo "$rows" >> tmp11-videos.csv
done

csvjoin tmp3-videos.csv tmp11-videos.csv > tmp12-videos.csv
rm tmp3-videos.csv tmp11-videos.csv
