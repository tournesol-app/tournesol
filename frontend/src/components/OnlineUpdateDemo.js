/* eslint no-unused-vars: ["error", { "argsIgnorePattern": "^_" }] */

import React from 'react';
import { useParams } from 'react-router-dom';
import { makeStyles } from '@material-ui/core/styles';
import Alert from '@material-ui/lab/Alert';
import InputLabel from '@material-ui/core/InputLabel';
import FormControl from '@material-ui/core/FormControl';
import Slider from '@material-ui/core/Slider';
import Select from '@material-ui/core/Select';
import LinearProgress from '@material-ui/core/LinearProgress';
import { TournesolAPI } from '../api';

import { featureList, featureNames } from '../constants';

const useStyles = makeStyles((theme) => ({
  root: {
    display: 'flex',
    width: '900px',
    maxWidth: '100%',
    height: '100%',
    overflowY: 'auto',
    overflowX: 'hidden',
    flexDirection: 'column',
    padding: '8px',
  },
  formControl: {
    margin: theme.spacing(1),
    minWidth: 120,
  },
  selectEmpty: {
    marginTop: theme.spacing(2),
  },
  noAnimation: {
    transition: 'none',
  },
}));

export default () => {
  const { videoIdA, videoIdB } = useParams();

  const classes = useStyles();

  const [v1Score, setV1Score] = React.useState(0);
  const [v2Score, setV2Score] = React.useState(0);
  const [v1ScoreAgg, setV1ScoreAgg] = React.useState(0);
  const [v2ScoreAgg, setV2ScoreAgg] = React.useState(0);
  const [feature, setFeature] = React.useState(featureList[0]);
  const [currentScore, setCurrentScore] = React.useState(50);
  const [error, setError] = React.useState(null);
  const [debugInfo, setDebugInfo] = React.useState(null);
  const [initialRequested, setInitialRequested] = React.useState(false);
  const [onlineRequested, setOnlineRequested] = React.useState(false);

  const modelRating = 1 / (1 + Math.exp(v1Score - v2Score));
  const modelAggRating = 1 / (1 + Math.exp(v1ScoreAgg - v2ScoreAgg));

  const getCurrentRating = () => {
    const api = new TournesolAPI.ExpertRatingsApi();
    api.expertRatingsByVideoIdsRetrieve(videoIdA, videoIdB, (err, data) => {
      if (err) {
        setError('Rating does not exist.');
      } else {
        let f = data[feature];
        if (f === null || f === undefined) {
          f = 50;
          setError('Feature was not defined in rating, setting to 50');
        }
        setCurrentScore(f);
      }
    });
  };

  const getAggVideoScore = (vId, callback) => {
    const api = new TournesolAPI.VideosApi();
    api.videosList({ videoId: vId }, (err, data) => {
      if (err || data.count !== 1) {
        setError('Video not found');
      } else {
        callback(data.results[0][feature]);
      }
    });
  };

  const getMyVideoScore = (vId, callback) => {
    const api = new TournesolAPI.VideoRatingsApi();
    api.videoRatingsList({ videoVideoId: vId }, (err, data) => {
      if (err || data.count !== 1) {
        setError('Video rating not found');
      } else {
        callback(data.results[0][feature]);
      }
    });
  };

  if (initialRequested === false) {
    setInitialRequested(true);
    getCurrentRating();
    getAggVideoScore(videoIdA, setV1ScoreAgg);
    getAggVideoScore(videoIdB, setV2ScoreAgg);
    getMyVideoScore(videoIdA, setV1Score);
    getMyVideoScore(videoIdB, setV2Score);
  }

  const onlineUpdate = (val) => {
    if (onlineRequested) {
      return;
    }
    setOnlineRequested(true);
    const api = new TournesolAPI.ExpertRatingsApi();
    api.expertRatingsOnlineByVideoIdsRetrieve(feature, val, videoIdA, videoIdB,
      { addDebugInfo: true }, (err, data) => {
        if (err) {
          setError('Online update failed');
        } else {
          setV1Score(data.new_score_left);
          setV2Score(data.new_score_right);
          setV1ScoreAgg(data.agg_score_left);
          setV2ScoreAgg(data.agg_score_right);
          setDebugInfo({ ...data, debug_info: JSON.parse(data.debug_info) });
        }
        setOnlineRequested(false);
      });
  };

  return (
    <div style={{ width: '500px' }}>
      Comparing videos {videoIdA}, {videoIdB}

      {error !== null && (
        <Alert severity="error">
          {error}
        </Alert>)}

      {debugInfo !== null && (
        <Alert severity="info">
          <pre>
            {JSON.stringify(debugInfo, null, 4)}
          </pre>
        </Alert>)}

      <br />

      Select a feature:
      {/* Feature selector */}
      <div>
        <FormControl className={classes.formControl}>
          <InputLabel id="demo-simple-select-label">Feature</InputLabel>
          <Select
            labelId="demo-simple-select-label"
            id="demo-simple-select"
            value={feature}
            onChange={(e) => {
              setFeature(e.target.value);
              setInitialRequested(false);
            }}
          >
            {featureList.map((f) => <option value={f}>{featureNames[f]}</option>)}
          </Select>
        </FormControl>
      </div>

      <br />

      Input the value
      {/* Input slider */}
      <Slider
        value={currentScore}
        onChange={(_ev, val) => {
          setCurrentScore(val);
          onlineUpdate(val);
        }}
        min={0}
        max={100}
      />

      <br />

      My comparison:
      <LinearProgress className={classes.noAnim} value={modelRating * 100} variant="determinate" />

      <br />

      Aggregated model comparison:
      <LinearProgress
        className={classes.noAnim}
        value={modelAggRating * 100}
        variant="determinate"
      />

      <br />

    </div>);
};
