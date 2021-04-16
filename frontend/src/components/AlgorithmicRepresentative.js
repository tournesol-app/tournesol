import React from 'react';

import { makeStyles } from '@material-ui/core/styles';
import Chart from 'react-google-charts';
import { TournesolAPI } from '../api';

import { featureColors, featureList, featureNames, SEARCH_FEATURE_CONST_ADD } from '../constants';

const useStyles = makeStyles(() => ({
  root: {
    display: 'flex',
    flexFlow: 'column',
    border: '2px solid black',
    padding: '4px',
    margin: '4px',
    alignItems: 'center',
    width: '400px',
  },
  chartContainer: {
    width: '300px',
    height: '240px',
  },
}));

export default ({ videoId, overrideFeature = null, overrideValue = null }) => {
  const classes = useStyles();
  const [numRatings, setNumRatings] = React.useState(0);
  const [dataRequested, setDataRequested] = React.useState(false);
  const [dataFound, setDataFound] = React.useState(false);
  const [chartData, setChartData] = React.useState([]);

  const chartDataPrefix = [
    [
      'Property',
      'Rating',
      { role: 'style' },
      {
        sourceColumn: 0,
        role: 'annotation',
        type: 'string',
        calc: 'stringify',
      },
    ],
  ];

  if (!dataRequested) {
    setDataRequested(true);
    const apiRating = new TournesolAPI.ExpertRatingsApi();
    apiRating.expertRatingsList({ videoVideoId: videoId, limit: 1 }, (err, res) => {
      if (!err) {
        setNumRatings(res.count);
      }
    });
    const apiVideo = new TournesolAPI.VideoRatingsApi();
    apiVideo.videoRatingsList({ videoVideoId: videoId, limit: 1 }, (err, res) => {
      if (!err && res.count === 1) {
        const data = res.results[0];
        const chartDataNew = chartDataPrefix;
        setDataFound(true);
        Object.keys(featureNames).forEach((k) => {
          chartDataNew.push([featureNames[k], data[k] + SEARCH_FEATURE_CONST_ADD,
            featureColors[k], null]);
        });
        setChartData(chartDataNew);
        // console.log(chartDataNew);
      }
    });
  }

  // if an override value is present, use it
  const chartDataWithOverride = chartData;
  if (overrideFeature) {
    const fIdx = featureList.indexOf(overrideFeature);
    let val = overrideValue + SEARCH_FEATURE_CONST_ADD;
    if (val < 0) {
      val = 0;
    }
    if (val > 2) {
      val = 2;
    }
    chartDataWithOverride[fIdx + 1][1] = val;
  }

  return (
    <>{dataFound ? (
      <div className={classes.root}>
        <span style={{ fontSize: '120%' }}>
          Based on {numRatings} ratings of the video, our model estimated that you would give
          the following scores:
        </span>
        <div className={classes.chartContainer}>
          <Chart
            width="100%"
            height="100%"
            chartType="BarChart"
            loader={<div>Loading ...</div>}
            data={chartDataWithOverride}
            options={{
              bar: { groupWidth: '80%' },
              vAxis: { textPosition: 'none' },
              chartArea: { width: '95%', height: '95%' },
              hAxis: { minValue: 0, maxValue: 2 },
            }}
          />
        </div>
      </div>
    ) : <p>Scores from your representative for this video are not yet available</p>}
    </>);
};
