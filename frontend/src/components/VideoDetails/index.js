import React from 'react';

import { useParams, useHistory } from 'react-router-dom';
import { makeStyles } from '@material-ui/core/styles';
import Grid from '@material-ui/core/Grid';
import Alert from '@material-ui/lab/Alert';
import Plot from 'react-plotly.js';
import IconButton from '@material-ui/core/IconButton';
import SkipPreviousIcon from '@material-ui/icons/SkipPrevious';
import SkipNextIcon from '@material-ui/icons/SkipNext';
import { featureNames, featureColors, featureList } from '../../constants';
import FeatureSelector from '../VideoComments/FeatureSelector';
import VideoCard from '../VideoCard';
import VideoSelector from '../ExpertInterface/VideoSelector';
import VideoComments from '../VideoComments';
import AlgorithmicRepresentative from '../AlgorithmicRepresentative';
import ExpertInterface from '../ExpertInterface/index';
import { GET_VIDEO_FOR_COMPARISON, GET_VIDEO, TournesolAPI } from '../../api';

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

// iterate over the comparisons in random order
const ComparisonSelector = ({
  videoId,
  onComparisonChanged = null,
  maxRatings = 1000,
  child,
}) => {
  // number of comparisons (ratings)
  const [count, setCount] = React.useState(undefined);

  // for which video was the count requested?
  const [countForVideo, setCountForVideo] = React.useState(null);

  // array of offsets (shuffled range 0..|ratings|-1)
  const [ratingOffsetArray, setRatingOffsetArray] = React.useState(null);

  // internal offset state
  const [offset, setOffset] = React.useState(0);

  // rating offset that was requested last
  const [offsetRequested, setOffsetRequested] = React.useState(null);

  // resulting current rating
  const [rating, setRating] = React.useState(null);

  // are there more ratings than we are displaying?
  const [overflow, setOverflow] = React.useState(false);

  // there are some ratings
  const countValid = count !== undefined && count !== null && count > 0;

  // console.log(ratingOffsetArray, offset, rating,
  //  overflow, count, countForVideo, offsetRequested);

  if (videoId && videoId !== countForVideo) {
    setCountForVideo(videoId);
    setCount(null);
    setRatingOffsetArray(null);
    setOffset(0);
    setOffsetRequested(null);
    setRating(null);
    setOverflow(false);
  }

  // requesting the count if not requested before
  if (count === null) {
    setCount(undefined);

    const api = new TournesolAPI.ExpertRatingsApi();
    api.expertRatingsList({ limit: 1, videoVideoId: videoId }, (err, data) => {
      if (!err) {
        setCount(data.count);
      }
    });
  }

  // shuffle an array https://javascript.info/task/shuffle
  function shuffle(array) {
    array.sort(() => Math.random() - 0.5);
  }

  // filling ratingOffsetArray
  if (countValid && ratingOffsetArray === null) {
    // never greater than maxRatings to prevent memory issues in extreme cases
    const safeCount = Math.min(maxRatings, count);

    // overflow if there are more than we can show
    if (safeCount < count) {
      setOverflow(true);
    }

    const array = [...Array(safeCount).keys()];
    shuffle(array);
    setRatingOffsetArray(array);
  }

  // if there is a new offset that we can load, but it's not loaded yet
  if (
    ratingOffsetArray &&
    countValid &&
    offset !== offsetRequested &&
    offset >= 0 &&
    offset < ratingOffsetArray.length
  ) {
    setOffsetRequested(offset);

    // requesting the data...
    const api = new TournesolAPI.ExpertRatingsApi();
    api.expertRatingsList(
      { videoVideoId: videoId, limit: 1, offset: ratingOffsetArray[offset] },
      (err, data) => {
        if (!err && data.count >= 1) {
          const r = data.results[0];
          setRating(r);

          // console.log(r);

          if (onComparisonChanged) {
            onComparisonChanged(r);
          }
        }
      },
    );
  }

  if (countValid && ratingOffsetArray !== null) {
    return (
      <div>
        <span>
          You compared the video {ratingOffsetArray.length}
          {overflow ? '+' : ''} times. Showing rating{' '}
          {ratingOffsetArray[offset] + 1}/{ratingOffsetArray.length}.
        </span>

        <Grid
          container
          direction="row"
          justify="space-between"
          alignItems="center"
        >
          {/* left button */}
          <Grid item>
            <IconButton
              aria-label="left"
              color="primary"
              variant="outlined"
              onClick={() => {
                setOffset(offset - 1);
              }}
              disabled={offset <= 0}
            >
              <SkipPreviousIcon />
            </IconButton>
          </Grid>

          <Grid item>{child(rating)}</Grid>

          {/* right button */}
          <Grid item>
            <IconButton
              aria-label="left"
              color="primary"
              variant="outlined"
              onClick={() => {
                setOffset(offset + 1);
              }}
              disabled={offset + 1 >= ratingOffsetArray.length}
            >
              <SkipNextIcon />
            </IconButton>
          </Grid>
        </Grid>
      </div>
    );
  }

  return <span>You have not yet compared this video with others</span>;
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
  const [updatePending, setUpdatePending] = React.useState(false);

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

  const onlineUpdateFeed = (videoId1, videoId2, feature, value) => {
    if (updatePending) {
      return;
    }
    setUpdatePending(true);

    const api = new TournesolAPI.ExpertRatingsApi();
    api.expertRatingsOnlineByVideoIdsRetrieve(
      feature,
      value,
      videoId1,
      videoId2,
      { addDebugInfo: false },
      (err, data) => {
        if (!err) {
          // console.log(data);
          const newScore =
            videoId1 === videoId ? data.new_score_left : data.new_score_right;
          setOverrideFeature(feature);
          setOverrideValue(newScore);
        }
        setUpdatePending(false);
      },
    );
  };

  return (
    <div className={classes.root}>
      <div className={classes.titleContainer}>
        <span style={{ fontSize: '300%' }}>Video Analysis</span>
        <span style={{ fontSize: '120%' }}>Choose a video to be analyzed</span>
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
      </div>
      {infoLoading && <span>Loading...</span>}
      {!infoLoading && videoInfo && (
        <>
          <VideoCard video={videoInfo} showRatingsLink />
          <Grid container direction="row" spacing={3}>
            <Grid item>
              <div className={classes.container}>
                <VideoComments videoId={videoId} />
              </div>
            </Grid>
          </Grid>
        </>
      )}

      {!videoInfo && !infoLoading && videoId !== '...' && (
        <Alert severity="warning" style={{ margin: '8px' }}>
          This video has not been reviewed yet
        </Alert>
      )}

      <Grid container direction="column" spacing={3}>
        <Grid item>
          {!infoLoading && statistics.length > 0 && (
            <StatisticsHistogramSelectable statistics={statistics} />
          )}
        </Grid>

        <Grid item>
          {!infoLoading && (
            <div className={classes.container} style={{ direction: 'row' }}>
              <ComparisonSelector
                onComparisonChanged={() => {
                  setOverrideFeature(null);
                  setOverrideValue(null);
                }}
                style={{ width: '100%' }}
                videoId={videoId}
                child={(rating) => {
                  if (rating) {
                    return (
                      <ExpertInterface
                        videoIdAOverride={rating.video_1}
                        showControls={false}
                        style={{ width: '90%' }}
                        videoIdBOverride={rating.video_2}
                        onSliderFeatureChanged={(feature, value) => onlineUpdateFeed(
                          rating.video_1,
                          rating.video_2,
                          feature,
                          value,
                        )}
                        key={`rating-${rating.id}`}
                      />
                    );
                  }

                  return <span>Loading...</span>;
                }}
              />
            </div>
          )}
        </Grid>

        {!infoLoading && videoInfo && (
          <Grid item>
            <AlgorithmicRepresentative
              overrideFeature={overrideFeature}
              overrideValue={overrideValue}
              videoId={videoId}
            />
          </Grid>
        )}
      </Grid>
    </div>
  );
};
