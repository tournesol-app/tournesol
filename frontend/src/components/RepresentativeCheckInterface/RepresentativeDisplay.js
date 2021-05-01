import React, { useState } from 'react';

import YouTube from 'react-youtube';
import { makeStyles } from '@material-ui/core/styles';
import Slider from '@material-ui/core/Slider';
import Button from '@material-ui/core/Button';
import Tooltip from '@material-ui/core/Tooltip';
import IconButton from '@material-ui/core/IconButton';
import CommentIcon from '@material-ui/icons/Comment';

import { featureNames } from '../../constants';
import { TournesolAPI, UPDATE_COMPARISON } from '../../api';

const useStyles = makeStyles(() => ({
  root: {
    width: '100%',
    display: 'flex',
    justifyContent: 'center',
    overflow: 'hidden',
  },
  centered: {
    width: '750px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    flex: '0 0 auto',
  },
  comparisonContainer: {
    display: 'flex',
    flexDirection: 'row',
    margin: '8px',
    width: '750px',
    textAlign: 'center',
  },
  videoContainer: {
    position: 'relative',
    height: '140px',
    width: '250px',
    background: '#000',
    flex: 0,
  },
  featureDisplayContainer: {
    display: 'flex',
    flexDirection: 'column',
    paddingTop: '32px',
    flex: 1,
    margin: '8px',
    justifyContent: 'center',
    alignItem: 'center',
  },
  sliderModelRail: {
    color: 'red',
  },
  sliderModelThumb: {
    color: 'red',
  },
  floatLeft: {
    left: '-36px',
    position: 'absolute',
    top: '0px',
    display: 'flex',
    flexDirection: 'column',
  },
  floatRight: {
    right: '-42px',
    position: 'absolute',
    top: '0px',
    display: 'flex',
    flexDirection: 'column',
  },
  commentContainer: {
    display: 'flex',
    flexDirection: 'column',
    flex: '1 1 auto',
    border: '1px solid black',
    overflowY: 'auto',
    overflowX: 'hidden',
    padding: '4px',
    margin: '4px',
  },
  sliderContainer: {
    display: 'flex',
    flexDirection: 'column',
    width: '600px',
    alignItems: 'center',
  },
}));

const Buttons = ({ videoId, _class, commentsOpen, setCommentsOpen }) => (
  <div className={_class}>
    <Tooltip title="Comments" aria-label="add">
      <IconButton
        size="small"
        aria-label="load"
        onClick={() => {
          setCommentsOpen(commentsOpen === videoId ? undefined : videoId);
        }}
      >
        <CommentIcon size="small" />
      </IconButton>
    </Tooltip>
  </div>
);

const Comparison = (props) => {
  const { videoA, videoB, feature } = props;
  const { commentsLeftOpen, setCommentsLeftOpen } = props;
  const { commentsRightOpen, setCommentsRightOpen } = props;
  const classes = useStyles();

  const opts = {
    height: '140px',
    width: '250px',
    playerVars: {
      // https://developers.google.com/youtube/player_parameters
      autoplay: 0,
    },
  };

  return (
    <div className={classes.comparisonContainer}>
      <div className={classes.videoContainer}>
        {window.ENABLE_YOUTUBE_VIDEO_EMBED === 1 ? (
          <YouTube videoId={videoA} opts={opts} />
        ) : (
          <span>Youtube {videoA}</span>
        )}

        <Buttons
          videoId={videoA}
          _class={classes.floatRight}
          commentsOpen={commentsLeftOpen}
          setCommentsOpen={setCommentsLeftOpen}
        />
      </div>
      <div className={classes.featureDisplayContainer}>
        <span style={{ fontSize: '160%' }}>{featureNames[feature]}</span>
      </div>
      <div className={classes.videoContainer}>
        {window.ENABLE_YOUTUBE_VIDEO_EMBED === 1 ? (
          <YouTube videoId={videoB} opts={opts} />
        ) : (
          <span>Youtube {videoB}</span>
        )}

        <Buttons
          videoId={videoB}
          _class={classes.floatLeft}
          commentsOpen={commentsRightOpen}
          setCommentsOpen={setCommentsRightOpen}
        />
      </div>
    </div>
  );
};

export default ({
  next,
  disagreement,
  commentsLeftOpen,
  setCommentsLeftOpen,
  commentsRightOpen,
  setCommentsRightOpen,
}) => {
  const { feature, modelScore, expertScore, videoA, videoB } = disagreement;
  const [newExpertScore, setNewExpertScore] = useState(null);
  const [isUpdated, setIsUpdated] = useState(false);
  const classes = useStyles();

  const [timer, setTimer] = React.useState(new Date());
  const [sliderChangeEnabled, setSliderChangeEnabled] = React.useState(true);

  const timerBegin = () => {
    setTimer(new Date());
  };

  if (timer === null) {
    timerBegin();
  }

  const timerGet = () => new Date() - timer;

  // send current slider values to the server for statistics
  const registerSliderChange = (val) => {
    if (!sliderChangeEnabled) return;
    setSliderChangeEnabled(false);
    const api = new TournesolAPI.ExpertRatingsApi();
    api.registerSliderChange(
      {
        video_left: videoA,
        video_right: videoB,
        duration_ms: timerGet(),
        context: 'DIS',
        [feature]: val,
      },
      () => {
        setSliderChangeEnabled(true);
      },
    );
  };

  return (
    <>
      <Comparison
        key={videoA}
        videoA={videoA}
        videoB={videoB}
        commentsLeftOpen={commentsLeftOpen}
        setCommentsLeftOpen={setCommentsLeftOpen}
        commentsRightOpen={commentsRightOpen}
        setCommentsRightOpen={setCommentsRightOpen}
        feature={feature}
      />
      <div className={classes.sliderContainer}>
        <span>The score that our model thinks you would give</span>
        <Slider
          aria-label="custom thumb label"
          color="secondary"
          value={modelScore}
          track={false}
          classes={{
            rail: classes.sliderModelRail,
            thumb: classes.sliderModelThumb,
          }}
          disabled
        />
        <span>The score that you gave</span>
        <Slider
          className="representative_debug_slider"
          aria-label="custom thumb label"
          color="secondary"
          value={newExpertScore === null ? expertScore : newExpertScore}
          track={false}
          onChange={(e, value) => {
            setNewExpertScore(value);
            setIsUpdated(true);
            registerSliderChange(value);
          }}
        />
      </div>
      <Button
        className="representative_debug_submit"
        variant="contained"
        size="large"
        color="primary"
        style={{
          margin: '16px',
          backgroundColor: isUpdated ? undefined : 'red',
        }}
        onClick={() => {
          setNewExpertScore(null);
          setCommentsLeftOpen(false);
          setCommentsRightOpen(false);
          setIsUpdated(false);
          if (newExpertScore) {
            UPDATE_COMPARISON({
              video_1: videoA,
              video_2: videoB,
              [feature]: newExpertScore,
            });
          }
          next();
        }}
      >
        {isUpdated ? 'Update Rating' : 'Ignore'}
      </Button>
    </>
  );
};
