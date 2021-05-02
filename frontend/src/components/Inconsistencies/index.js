import React, { useState } from 'react';

import { makeStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import Slider from '@material-ui/core/Slider';
import Button from '@material-ui/core/Button';
import Tooltip from '@material-ui/core/Tooltip';
import IconButton from '@material-ui/core/IconButton';
import CommentIcon from '@material-ui/icons/Comment';

import YouTube from 'react-youtube';

import VideoComments from '../VideoComments';
import { UPDATE_COMPARISON, TournesolAPI } from '../../api';

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
  sliderContainer: {
    display: 'flex',
    flexDirection: 'column',
    paddingTop: '32px',
    flex: 1,
    margin: '8px',
    justifyContent: 'center',
    alignItem: 'center',
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
}));

const Buttons = ({ videoId, _class, setOpenComments }) => (
  <div className={_class}>
    <Tooltip title="Comments" aria-label="add">
      <IconButton
        size="small"
        aria-label="load"
        onClick={() => setOpenComments(videoId)}
      >
        <CommentIcon size="small" />
      </IconButton>
    </Tooltip>
  </div>
);

const Comparison = (props) => {
  const { videoA, videoB, feature } = props;
  const { score, setScore, setOpenComments } = props;

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
        context: 'INC',
        [feature]: val,
      },
      () => {
        setSliderChangeEnabled(true);
      },
    );
  };

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
    <div
      className={`${classes.comparisonContainer} inconsistency`}
      id={`${videoA}_${videoB}`}
    >
      <div className={classes.videoContainer}>
        {window.ENABLE_YOUTUBE_VIDEO_EMBED === 1 ? (
          <YouTube videoId={videoA} opts={opts} />
        ) : (
          <span>Youtube {videoA}</span>
        )}

        <Buttons
          videoId={videoA}
          _class={classes.floatRight}
          setOpenComments={(x) => setOpenComments('left', x)}
        />
      </div>
      <div className={classes.sliderContainer}>
        <span>{feature}</span>
        <Slider
          className="inconsistency_slider"
          aria-label="custom thumb label"
          color="secondary"
          value={score}
          track={false}
          onChange={(e, value) => {
            registerSliderChange(value);
            setScore(value);
            return null;
          }}
        />
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
          setOpenComments={(x) => setOpenComments('right', x)}
        />
      </div>
    </div>
  );
};

const InconsistencyDisplay = ({
  inconsistency,
  setInconsistency,
  setOpenComments,
}) => {
  const { feature, comparisons } = inconsistency;

  return (
    <div>
      {comparisons.map(({ videoA, videoB, score }, i) => (
        <Comparison
          key={videoA}
          videoA={videoA}
          videoB={videoB}
          setOpenComments={setOpenComments}
          feature={feature}
          score={score}
          setScore={(s) => {
            comparisons[i].score = s;
            setInconsistency({ feature, comparisons });
          }}
        />
      ))}
    </div>
  );
};

export default () => {
  const classes = useStyles();

  const [inconsistencies, setInconsistencies] = useState(null);
  const [inconsistencyIndex, setInconsistencyIndex] = useState(0);
  const [commentsLeftOpen, setCommentsLeftOpen] = useState(undefined);
  const [commentsRightOpen, setCommentsRightOpen] = useState(undefined);
  const [loading, setLoading] = useState(false);

  const setOpenComments = (side, videoId) => {
    setCommentsLeftOpen(
      side === 'left' && videoId !== commentsLeftOpen && videoId,
    );
    setCommentsRightOpen(
      side === 'right' && videoId !== commentsRightOpen && videoId,
    );
  };

  const isFixed = (z) => {
    const [s1, s2, s3] = z.comparisons.map((x) => x.score).slice(0, 3);
    return s1 < 50 !== s2 < 50 || s1 < 50 !== s3 < 50;
  };

  if (!inconsistencies && !loading) {
    setLoading(true);
    const api = new TournesolAPI.ExpertRatingsApi();
    api.apiV2ExpertRatingsShowInconsistencies({}, (err, data) => {
      if (!err) {
        setInconsistencies(data.results);
      }
      setLoading(false);
    });

    return (
      <div className={classes.root}>
        <div className={classes.centered}>computing inconsistencies . . .</div>
      </div>
    );
  }

  const inconsistency =
    inconsistencies !== null && inconsistencies.length > 0
      ? inconsistencies[inconsistencyIndex]
      : null;
  const setInconsistency = (x) => {
    inconsistencies[inconsistencyIndex] = x;
    setInconsistencies([...inconsistencies]);
  };

  return (
    <div className={classes.root} id="id_all_inconsistencies">
      {commentsLeftOpen && (
        <div className={classes.commentContainer}>
          <VideoComments videoId={commentsLeftOpen} />
        </div>
      )}
      {!loading && <div id="id_inconsistencies_not_loading" />}
      <div className={classes.centered}>
        {inconsistency ? (
          <>
            <Typography variant="h4">
              You have {inconsistencies.length} inconsistenc
              {inconsistencies.length < 2 ? 'y' : 'ies'}
            </Typography>
            <Typography paragraph>
              Inconsistencies affect your voting powers negatively. We recommend
              that you fix them.
            </Typography>
          </>
        ) : (
          <>
            <Typography variant="h4">You have no inconsistencies.</Typography>
            <Typography paragraph>
              Visit this page again after having submitted more rating to make
              sure that your ratings are not inconsistent.
            </Typography>
          </>
        )}
        {inconsistency && (
          <>
            <Typography paragraph>
              ({1 + inconsistencyIndex} / {inconsistencies.length})
            </Typography>
            <InconsistencyDisplay
              inconsistency={inconsistency}
              setInconsistency={setInconsistency}
              setOpenComments={setOpenComments}
            />
            <Button
              className="inconsistency_submit"
              variant="contained"
              color="primary"
              style={{
                margin: '16px',
                backgroundColor: isFixed(inconsistency) ? '' : 'red',
              }}
              onClick={() => {
                setInconsistencyIndex(inconsistencyIndex + 1);
                const { feature, comparisons } = inconsistency;
                comparisons.forEach(({ videoA, videoB, score }) => {
                  UPDATE_COMPARISON({
                    video_1: videoA,
                    video_2: videoB,
                    [feature]: score,
                  });
                });
              }}
            >
              {isFixed(inconsistency) ? 'Submit Rating' : 'Ignore'}
            </Button>
          </>
        )}
      </div>
      {commentsRightOpen && (
        <div className={classes.commentContainer}>
          <VideoComments videoId={commentsRightOpen} />
        </div>
      )}
    </div>
  );
};
