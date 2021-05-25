import React from 'react';

import { useParams, useHistory } from 'react-router-dom';
import Plot from 'react-plotly.js';
import { makeStyles } from '@material-ui/core/styles';
import Grid from '@material-ui/core/Grid';
import Alert from '@material-ui/lab/Alert';
import Typography from '@material-ui/core/Typography';

import { featureNames, featureColors, featureList } from '../../constants';
import FeatureSelector from '../VideoComments/FeatureSelector';
import VideoCard from '../VideoCard';
import VideoSelector from '../ExpertInterface/VideoSelector';
import VideoComments from '../VideoComments';
import AlgorithmicRepresentative from '../AlgorithmicRepresentative';
import { GET_VIDEO_FOR_COMPARISON, GET_VIDEO, TournesolAPI } from '../../api';

import ComparisonSelector from './ComparisonSelector';

const useStyles = makeStyles(() => ({
  root: { display: 'flex', flexFlow: 'row wrap' },
  titleContainer: {
    margin: '4px',
    padding: '4px',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'space-around',
    flex: '0 0 auto',
  },
  container: {
    border: '2px solid black',
    padding: '4px',
    margin: '4px',
    maxWidth: '900px',
    maxHeight: '800px',
    overflow: 'auto',
  },
}));

// histogram for a fixed feature
const StatisticsHistogramChart = ({ statistics, feature }) => {
  const arr = statistics.map((x) => x[feature]);
  const color = featureColors[feature];
  const name = featureNames[feature];

  return (
    <Plot
      data={[
        {
          x: arr,
          y: arr,
          type: 'histogram',
          mode: 'lines+markers',
          marker: { color },
        },
      ]}
      layout={{ width: 550, height: 300, title: name }}
    />
  );
};

// histogram with a feature selector
const StatisticsHistogramSelectable = ({ statistics }) => {
  const [feature, setFeature] = React.useState(featureList[0]);

  const showInitial = {};
  featureList.forEach((f) => {
    showInitial[f] = false;
  });
  showInitial[feature] = true;

  const classes = useStyles();

  return (
    <div className={classes.container}>
      <span style={{ fontSize: '120%' }}>
        The histogram shows the distribution of the scores given by all experts,
        including you!
      </span>
      <FeatureSelector
        show={showInitial}
        readOnly={false}
        onUpdateSingle={setFeature}
        single
        minimalist={false}
      />
      <StatisticsHistogramChart statistics={statistics} feature={feature} />
    </div>
  );
};

export default () => {
  const classes = useStyles();
  const { videoId } = useParams();
  const history = useHistory();

  const [videoInfo, setVideoInfo] = React.useState(null);
  const [infoLoading, setInfoLoading] = React.useState(false);

  const [statistics, setStatistics] = React.useState([]);

  const [statisticsRequested, setStatisticsRequested] = React.useState(false);

  // online updates
  const [overrideFeature, setOverrideFeature] = React.useState(null);
  const [overrideValue, setOverrideValue] = React.useState(null);

  if (!statisticsRequested && videoId) {
    setStatisticsRequested(true);

    const api = new TournesolAPI.VideoRatingsApi();

    // todo: add selected features as parameters to compute the total score
    api.videoRatingStatistics(
      { videoVideoId: videoId, limit: 100 },
      (err, data) => {
        if (!err) {
          setStatistics(data.results);
          // console.log("statistics", data['results']);
        }
      },
    );
  }

  const loadVideo = (setVideoCallback) => {
    GET_VIDEO_FOR_COMPARISON(false, (v) => setVideoCallback(v));
  };

  const updateVideo = (v) => {
    setInfoLoading(true);
    setStatisticsRequested(false);
    setOverrideFeature(null);
    setOverrideValue(null);
    if (infoLoading === true || !v) return;
    GET_VIDEO(v, (x) => {
      setVideoInfo(x);
      setInfoLoading(false);
    });
  };

  if (
    videoId &&
    (videoInfo === null || videoInfo.video_id !== videoId) &&
    !infoLoading
  ) {
    updateVideo(videoId);
  }

  return (
    <div className={classes.root}>
      <Grid container spacing={3}>
        <Grid item xs={12} sm={3}>
          <Typography variant="h3">Video Analysis</Typography>
          <Typography paragraph>Choose a video to be analyzed</Typography>
          <VideoSelector
            id={videoId || '...'}
            setId={(x) => history.push(`/details/${x}`)}
            getNewId={() => {
              loadVideo((x) => history.push(`/details/${x}`));
            }}
            showPlayer={false}
            showCommentButton={false}
            showReport={false}
          />
        </Grid>
        <Grid item xs={12} sm={9}>
          {infoLoading ? <span>Loading...</span> : <VideoCard video={videoInfo} showRatingsLink />}
        </Grid>

        {!infoLoading && videoInfo && (
        <Grid item xs={12} sm={6}>
          <AlgorithmicRepresentative
            overrideFeature={overrideFeature}
            overrideValue={overrideValue}
            videoId={videoId}
          />
        </Grid>
        )}

        {!infoLoading && videoInfo && (
          <Grid item xs={12} sm={6}>
            <VideoComments videoId={videoId} />
          </Grid>
        )}

        {!videoInfo && !infoLoading && videoId !== '...' && (
        <Grid item xs={12} sm={6}>
          <Alert severity="warning" style={{ margin: '8px' }}>
            This video has not been reviewed yet
          </Alert>
        </Grid>
        )}

        {!infoLoading && statistics.length > 0 && (
        <Grid item xs={12} sm={6}>
          <StatisticsHistogramSelectable statistics={statistics} />
        </Grid>
        )}

        {!infoLoading && (
        <Grid item xs={12}>
          <ComparisonSelector
            onComparisonChanged={(feature, value) => {
              setOverrideFeature(feature);
              setOverrideValue(value);
            }}
            videoId={videoId}
          />
        </Grid>
        )}

      </Grid>
    </div>
  );
};
