import React, { useState } from 'react';

import { useHistory, useParams } from 'react-router-dom';
import { makeStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import IconButton from '@material-ui/core/IconButton';
import Slider from '@material-ui/core/Slider';
import Tooltip from '@material-ui/core/Tooltip';
import Button from '@material-ui/core/Button';
import InfoIcon from '@material-ui/icons/HelpOutline';
import DoubleArrowIcon from '@material-ui/icons/DoubleArrow';
import Alert from '@material-ui/lab/Alert';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogActions from '@material-ui/core/DialogActions';
import Dialog from '@material-ui/core/Dialog';
import SettingsIcon from '@material-ui/icons/Settings';
import Grid from '@material-ui/core/Grid';
import FormControl from '@material-ui/core/FormControl';
import FormLabel from '@material-ui/core/FormLabel';
import RadioGroup from '@material-ui/core/RadioGroup';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import Radio from '@material-ui/core/Radio';
import Checkbox from '@material-ui/core/Checkbox';
import Rating from '@material-ui/lab/Rating';
import SidePanel from './SidePanel';
import VideoSelector from './VideoSelector';
import { featureList, featureNames } from '../../constants';
import {
  GET_COMPARISON_RATING,
  SUBMIT_COMPARISON_RESULT,
  TournesolAPI,
  UPDATE_COMPARISON,
} from '../../api';
import Intro, { featureLinks } from './Intro';
import { TutorialTooltip } from './TutorialTooltips';

// variables starting with underscore can be unused
/* eslint no-unused-vars: ["error", { "argsIgnorePattern": "^_" }] */

const getDefaultComparison = () => {
  const c = {};
  featureList.forEach((f) => {
    c[f] = 50;
  });
  return c;
};

const getDefaultWeights = () => {
  const c = {};
  featureList.forEach((f) => {
    c[f] = 1;
  });
  return c;
};

const getDefaultSkipState = () => {
  const c = {};
  featureList.forEach((f) => {
    c[f] = false;
  });
  return c;
};

const getDefaultConfidence = () => {
  const c = {};
  featureList.forEach((f) => {
    c[f] = 2;
  });
  return c;
};

const useStyles = makeStyles(() => ({
  root: {
    width: '100%',
    display: 'flex',
    justifyContent: 'center',
    overflow: 'hidden',
  },
  centered: {
    paddingBottom: '32px',
    width: '880px',
    flex: '0 0 auto',
    maxWidth: '100%',
  },
  videoContainer: {
    display: 'flex',
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: '16px',
  },
  featuresContainer: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
  },
  sliderContainer: {
    display: 'flex',
    flexDirection: 'row',
    width: '620px',
    alignItems: 'center',
    margin: '-2px',
  },
  slider: {
    flex: '1 1 0px',
  },
  formControl: {
    width: '128px',
  },
  featureNameDisplay: {
    display: 'flex',
    flexDirection: 'row',
    alignItems: 'center',
  },
  clock: {
    display: 'flex',
    alignItems: 'center',
    float: 'right',
    color: 'gray',
  },
  alertTop: {
    marginBottom: '15px',
  },
}));

const ValueLabelComponent = (props) => {
  const { children, open, value } = props;

  const tooltipValue = [
    'Left is a lot better',
    'Left is a little better',
    'The videos are similar',
    'Right is a little better',
    'Right is a lot better',
  ][Math.floor((value / 100.001) * 5)];

  return (
    <Tooltip
      open={open}
      enterTouchDelay={0}
      placement="top"
      title={tooltipValue}
    >
      {children}
    </Tooltip>
  );
};

// https://openclassrooms.com/en/courses/4286486-build-web-apps-with-reactjs/4286711-build-a-ticking-clock-component
// class Clock extends React.Component {
//   constructor(props) {
//     super(props);
//     this.state = {
//       time: 0,
//     };
//   }

//   componentDidMount() {
//     this.intervalID = setInterval(() => this.tick(), 1000);
//   }

//   componentWillUnmount() {
//     clearInterval(this.intervalID);
//   }

//   tick() {
//     const { start } = this.props;
//     this.setState({
//       time: new Date() - start,
//     });
//   }

//   render() {
//     const { time } = this.state;
//     const ms = Math.round(time / 1000);
//     const mins = Math.floor(ms / 60);
//     const secs = ms % 60;
//     const zeroPad = (num, places) => String(num).padStart(places, '0');
//     return `${zeroPad(mins, 2)}:${zeroPad(secs, 2)}`;
//   }
// }

const ExpertSettings = ({ setStateExternal }) => {
  // const { setStateExternal } = useParams();
  const [state, setStateLocal] = React.useState(null);
  const [submittedStatus, setSubmittedStatus] = React.useState(null);

  const setState = (s) => {
    setStateLocal(s);
    if (s) {
      setStateExternal(s);
    }
  };

  if (state === null) {
    setState(undefined);
    const api = new TournesolAPI.UserPreferencesApi();
    api.userPreferencesMyRetrieve((err, data) => {
      if (!err) {
        setState(data);
      }
    });
  }

  const submitState = () => {
    setSubmittedStatus(null);
    const api = new TournesolAPI.UserPreferencesApi();
    api.userPreferencesMyPartialUpdate(
      { patchedUserPreferencesSerializerV2: state },
      (err, _data) => {
        if (err) {
          setSubmittedStatus(false);
        } else {
          setSubmittedStatus(true);
        }
      },
    );
  };

  return (
    <div>
      {(state === null || state === undefined) && <p>Loading...</p>}

      {submittedStatus === true && (
        <Alert severity="success" id="id_expert_settings_ok">
          Data saved
        </Alert>
      )}
      {submittedStatus === false && (
        <Alert severity="error" id="id_expert_settings_error">
          Error saving data
        </Alert>
      )}

      {state !== null && state !== undefined && (
        <div id="id_state_expert_settings_form">
          <FormControl component="fieldset">
            <FormLabel component="legend">
              Which quality features would you like to rate?
            </FormLabel>

            {featureList.map((f) => {
              const key = `${f}_enabled`;
              return (
                <FormControlLabel
                  control={
                    <Checkbox
                      id={`id_checkbox_${key}`}
                      checked={state[key]}
                      onChange={(e) => {
                        const newState = { ...state };
                        newState[key] = e.target.checked;
                        setState(newState);
                      }}
                      name={key}
                      color="primary"
                    />
                  }
                  label={featureNames[f]}
                />
              );
            })}
          </FormControl>

          <hr />

          <FormControl component="fieldset">
            <FormLabel component="legend">
              Would you like to report your confidence?
            </FormLabel>
            <RadioGroup
              aria-label="rating_mode"
              name="rating_mode"
              value={state.rating_mode}
              onChange={(e) => {
                setState({ ...state, rating_mode: e.target.value });
              }}
            >
              <FormControlLabel
                value="enable_all"
                control={<Radio id="id_enable_all" />}
                label="No confidence option"
              />
              <FormControlLabel
                value="skip"
                control={<Radio id="id_skip" />}
                label="Add a skip option"
              />
              <FormControlLabel
                value="confidence"
                control={<Radio id="id_confidence" />}
                label="Add a confidence option"
              />
            </RadioGroup>
          </FormControl>

          <hr />

          <FormControl component="fieldset">
            <Button
              variant="contained"
              color="primary"
              onClick={submitState}
              id="id_expert_settings_submit"
            >
              Submit
            </Button>
          </FormControl>
        </div>
      )}
    </div>
  );
};

export default ({ videoIdAOverride = null, videoIdBOverride = null,
  onSliderFeatureChanged = null, showControls = true }) => {
  // got a correct video Id?
  const isIdValid = (videoId) => {
    const notNull = videoId !== null;
    const notDots = videoId !== '...';
    const notUndefined = videoId !== undefined;
    return notNull && notDots && notUndefined && videoId;
  };

  const classes = useStyles();
  const { videoIdA = videoIdAOverride, videoIdB = videoIdBOverride } = useParams();

  const history = useHistory();

  const [showIntro, setShowIntro] = useState(false);
  const [videoA, setVideoARaw] = useState(
    !isIdValid(videoIdA) ? null : videoIdA,
  );
  const [videoB, setVideoBRaw] = useState(
    !isIdValid(videoIdB) ? null : videoIdB,
  );
  const [lastRatingMode, setLastRatingMode] = useState(null);
  const [comparison, setComparison] = useState(getDefaultComparison());
  const [weights, setWeights] = useState(getDefaultWeights());
  const [submitted, setSubmitted] = useState(false);
  const [editing, setEditing] = useState(false);
  const [error, setError] = useState('');
  const [timer, setTimer] = useState(new Date());
  const [needLoadRating, setNeedLoadRating] = useState(true);
  const [commentsOpen, setCommentsOpen] = useState('none');
  const [skippedA, setSkippedA] = useState([]);
  const [skippedB, setSkippedB] = useState([]);
  const [pending, setPending] = useState(false);
  const [sliderChangeEnabled, setSliderChangeEnabled] = useState(true);
  const [formOpen, setFormOpen] = React.useState(false);
  const [state, setState] = React.useState(null);
  const [skipState, setSkipState] = React.useState(getDefaultSkipState());
  const [confidenceState, setConfidenceState] = React.useState(
    getDefaultConfidence(),
  );
  const [confidenceStateHover, setConfidenceStateHover] = React.useState(
    getDefaultConfidence(),
  );
  const [videoAError, setVideoAError] = React.useState(null);
  const [videoBError, setVideoBError] = React.useState(null);
  const [needRefreshA, setNeedRefreshA] = React.useState(false);
  const [needRefreshB, setNeedRefreshB] = React.useState(false);
  const [submitPending, setSubmitPending] = React.useState(false);
  const [tourIndex, setTourIndex] = useState(-1);
  const [commentError, setCommentError] = useState(false);
  const [firstHistoryPush, setFirstHistoryPush] = useState(true);
  const [lastHistoryURL, setLastHistoryURL] = useState(null);

  // console.log("render", videoIdA, videoIdB, videoA, videoB);

  // updating internal IDs from the URL
  React.useEffect(() => {
    if (isIdValid(videoIdA) && (videoIdA !== videoA)) {
      setVideoARaw(videoIdA);
    }
    if (isIdValid(videoIdB) && (videoIdB !== videoB)) {
      setVideoBRaw(videoIdB);
    }
  }, [videoIdA, videoIdB]);

  const closeForm = () => {
    setFormOpen(false);
    // refresh everything?
  };

  const descriptionElementRef = React.useRef(null);
  React.useEffect(() => {
    if (formOpen) {
      const { current: descriptionElement } = descriptionElementRef;
      if (descriptionElement !== null) {
        descriptionElement.focus();
      }
    }
  }, [formOpen]);

  const timerBegin = () => {
    setTimer(new Date());
  };

  const timerGet = () => new Date() - timer;

  // send current slider values to the server for statistics
  const registerSliderChange = (currentComparison) => {
    if (!sliderChangeEnabled) return;
    setSliderChangeEnabled(false);
    const api = new TournesolAPI.ExpertRatingsApi();
    api.registerSliderChange(
      {
        video_left: videoA,
        video_right: videoB,
        duration_ms: timerGet(),
        context: 'RATE',
        ...currentComparison,
      },
      () => {
        setSliderChangeEnabled(true);
      },
    );
  };

  // STARS config
  const nStars = 3;
  const confidenceLabels = {
    0: 'Skip',
    1: 'Unsure',
    2: 'Somewhat confident',
    3: 'Extremely confident',
  };
  const STARS_TO_WEIGHT_COEFF = 0.5;

  // need comment for at least one of the videos?
  const MIN_RATING_DELTA_NEED_COMMENT_MAX_STARS = 5;
  const needOneCommentMaxStars = Math.max(
    ...Object.keys(confidenceState).filter((k) => Math.abs(comparison[k] - 50) >
          MIN_RATING_DELTA_NEED_COMMENT_MAX_STARS)
      .map((k) => confidenceState[k]),
  ) >= nStars;

  // are comments present for one of the videos?
  const commentsPresent = (videoId, cb) => {
    const api = new TournesolAPI.VideoCommentsApi();
    api.videoCommentsList({ limit: 1,
      videoVideoId: videoId,
      userUserUsername: window.username }, (err, data) => {
      if (err) {
        cb(false);
      } else {
        cb(data.count > 0);
      }
    });
  };

  const updateExistingRating = (videoA_, videoB_) => {
    if (videoA_ && videoB_) {
      setPending(true);
      GET_COMPARISON_RATING(
        videoA_,
        videoB_,
        (r) => {
          const newComparison = getDefaultComparison();
          const w = {};
          const confidenceStateUpdate = {};
          const skippedUpdate = {};
          featureList.map((key) => {
            if (r[key] !== undefined && r[key] !== null) {
              newComparison[key] = r[key];
              w[key] = r[`${key}_weight`];

              skippedUpdate[key] = !w[key];
              confidenceStateUpdate[key] = w[key] / STARS_TO_WEIGHT_COEFF;
            } else {
              newComparison[key] = 50;
              skippedUpdate[key] = true;

              // in ENABLE_ALL, all features have a weight of 1
              if (state.rating_mode === 'enable_all') {
                w[key] = 1.0;
              } else {
                w[key] = 0.0;
              }
              confidenceStateUpdate[key] = 0.0 / STARS_TO_WEIGHT_COEFF;
            }
            return null;
          });
          setConfidenceState(confidenceStateUpdate);
          setSkipState(skippedUpdate);
          setWeights(w);
          setComparison(newComparison);
          setEditing(true);
          setPending(false);
          return null;
        },
        () => {
          setEditing(false);
          setPending(false);
        },
      );
    }
    return null;
  };

  React.useEffect(() => {
    if (isIdValid(videoA) && isIdValid(videoB) && (videoIdA !== videoA || videoIdB !== videoB)) {
      const url = `/rate/${videoA}/${videoB}`;

      // only doing an update if the URL differs, to prevent duplicate entries in history
      if (lastHistoryURL !== url) {
      // console.log("changing URL to", url);

        setLastHistoryURL(url);

        // replace /rate to /rate/... to allow going back
        if (firstHistoryPush) {
          history.replace(url);
          setFirstHistoryPush(false);
        } else {
          history.push(url);
        }
      }
    }
  }, [videoA, videoB]);

  if (videoIdA && videoIdB && state !== null && state !== undefined) {
    if (state.rating_mode !== lastRatingMode) {
      setLastRatingMode(state.rating_mode);
      setNeedLoadRating(true);
    }
    if (needLoadRating) {
      setNeedLoadRating(false);
      setEditing(false);
      updateExistingRating(videoIdA, videoIdB);
    }
  }

  const getSubmitButtonName = () => {
    if (submitted) {
      return 'Edit rating';
    }
    return editing ? 'Submit edited rating' : 'Submit Rating';
  };

  const loadVideo = (setVideo, idx) => {
    setVideo('...');
    timerBegin();

    const idxToError = { 1: setVideoAError, 2: setVideoBError };

    const updateRating = (v) => {
      if (idx === 1) {
        updateExistingRating(v, videoB);
      } else if (idx === 2) {
        updateExistingRating(videoA, v);
      }
    };

    const onEmptyMsg = (
      <span className="class_sample_no_video">
        You can either add one of the videos from{' '}
        <Button
          variant="contained"
          size="small"
          color="primary"
          onClick={() => history.push('/recommendations')}
        >
          Search results
        </Button>{' '}
        to your{' '}
        <Button
          variant="contained"
          size="small"
          color="secondary"
          onClick={() => history.push('/rate_later')}
        >
          Rate later
        </Button>{' '}
        list, or copy-paste the URL of a new video you would like to rate. Note
        that you can use our{' '}
        <a href="https://chrome.google.com/webstore/detail/sunflower/nidimbejmadpggdgooppinedbggeacla?hl=en">
          browser extension
        </a>{' '}
        to import videos effortlessly
      </span>
    );

    const pleaseMore = (
      <span>
        You have provided ratings for all pairs of videos you imported.{' '}
        {onEmptyMsg}
      </span>
    );

    const pleaseAdd = <span>Your list of videos is empty. {onEmptyMsg}</span>;

    const errorConversion = {
      FIRST_RATED_AGAINST_ALL_RATED: pleaseMore,
      NO_FEATURES:
        'Please select some quality features to obtain video suggestions.',
      NO_RATE_LATER_NO_RATED: pleaseMore,
      NO_RATE_LATER_ALL_RATED: pleaseMore,
      NO_VIDEOS: pleaseAdd,
    };

    const processAPIError = (err) => {
      const errorDetail = JSON.parse(err.response.text).detail.toString();
      let errorMessage = errorDetail;

      Object.keys(errorConversion).forEach((v) => {
        if (errorDetail === v) {
          errorMessage = errorConversion[v];
        }
      });

      idxToError[idx](errorMessage);
    };

    const api = new TournesolAPI.ExpertRatingsApi();

    // set video data
    const processResult = (callback = null, ignoreSetErr = false) => (
      err,
      data,
    ) => {
      if (err) {
        if (!ignoreSetErr) {
          processAPIError(err);
        }
      } else {
        idxToError[idx](null);
        setVideo(data.video_id);
        updateRating(data.video_id);
      }
      if (callback !== null) {
        callback(err, data);
      }
    };

    // no video given -> sampling the first video...
    if (!isIdValid(videoA) && !isIdValid(videoB)) {
      if (idx === 2) {
        // NOT sampling the second video until there is the first one
        return;
      }
      api.expertRatingsSampleFirstVideoRetrieve({}, processResult(null));
    } else {
      // sampling based on the first video!
      const videoOther = idx === 1 ? videoB : videoA;

      // if got 404 (first video does not exist), sample like for the first one
      // because the first one is not in the system yet
      api.expertRatingsSampleVideoWithOtherRetrieve(
        videoOther,
        processResult((err, _data) => {
          if (err) {
            if (err.status === 404) {
              api.expertRatingsSampleFirstVideoRetrieve(
                { videoExclude: videoOther },
                processResult(null),
              );
            } else {
              processAPIError(err);
            }
          }
        }, true),
      );
    }

    setWeights(getDefaultWeights());
    setComparison(getDefaultComparison());
    setSubmitted(false);
    setError('');
  };

  const setVideoB = (v) => {
    setVideoBRaw(v);
    if (v) {
      setSkippedB([...skippedB, v]);
    }

    // no second video
    if (isIdValid(v) && !isIdValid(videoA)) {
      setNeedRefreshA(true);
    }
  };

  const setVideoA = (v) => {
    setVideoARaw(v);
    if (v) {
      setSkippedA([...skippedA, v]);
    }

    // no second video
    if (isIdValid(v) && !isIdValid(videoB)) {
      setNeedRefreshB(true);
    }
  };

  if (needRefreshA) {
    setNeedRefreshA(false);
    loadVideo(setVideoA, 1);
  }

  if (needRefreshB) {
    setNeedRefreshB(false);
    loadVideo(setVideoB, 2);
  }

  if (videoA === null) {
    loadVideo(setVideoA, 1);
  } else if (videoB === null) {
    loadVideo(setVideoB, 2);
  }

  const submitSkipped = () => {
    const skippedAsliced = skippedA.slice(0, -1);
    const skippedBsliced = skippedB.slice(0, -1);

    const api = new TournesolAPI.ExpertRatingsApi();
    if (skippedAsliced.length > 0) {
      api.expertRatingsSkipVideoPartialUpdate(skippedAsliced, (err, _data) => {
        if (!err) {
          if (skippedBsliced.length > 0) {
            api.expertRatingsSkipVideoPartialUpdate(skippedBsliced);
          }
        }
      });
    } else if (skippedBsliced.length > 0) {
      api.expertRatingsSkipVideoPartialUpdate(skippedBsliced);
    }
  };

  const submitComparisonReal = () => {
    setSubmitted(true);
    setSubmitPending(true);

    // to remove from Rate Later...
    const rateLaterApi = new TournesolAPI.RateLaterApi();

    submitSkipped();
    setSkippedA([]);
    setSkippedB([]);

    const comparisonSubmit = {
      video_1: videoA,
      video_2: videoB,
      duration_ms: timerGet(),
      ...comparison,
    };

    // adding weights
    featureList.forEach((f) => {
      comparisonSubmit[`${f}_weight`] = weights[f];
      return null;
    });

    // removing items that are not selected
    featureList.forEach((f) => {
      // a) not selected (state[f + "_enabled"] === false)
      if (!state[`${f}_enabled`]) {
        comparisonSubmit[`${f}_weight`] = 0.0;
      }
      return null;
    });

    if (editing) {
      UPDATE_COMPARISON(
        comparisonSubmit,
        (err) => {
          setError(err);
          setSubmitted(false);
          setSubmitPending(false);
        },
        () => {
          setSubmitPending(false);
          rateLaterApi.rateLaterBulkDeletePartialUpdate([
            { video_id: videoA },
            { video_id: videoB },
          ]);
        },
      );
    } else {
      setEditing(true);
      SUBMIT_COMPARISON_RESULT(
        null,
        comparisonSubmit,
        (err) => {
          setSubmitted(false);
          setError(err);
          setSubmitPending(false);
        },
        () => {
          setSubmitPending(false);
          rateLaterApi.rateLaterBulkDeletePartialUpdate([
            { video_id: videoA },
            { video_id: videoB },
          ]);
        },
      );
    }
  };

  const submitComparison = () => {
    setCommentError(false);
    if (needOneCommentMaxStars) {
      commentsPresent(videoIdA, (presA) => {
        if (presA) {
          submitComparisonReal();
        } else {
          commentsPresent(videoIdB, (presB) => {
            if (presB) {
              submitComparisonReal();
            } else {
              setCommentError(true);
            }
          });
        }
      });
    } else {
      submitComparisonReal();
    }
  };

  if (showIntro) {
    return (
      <div className={classes.root}>
        <div className={classes.centered}>
          <Typography variant="h3" noWrap>
            Content Rating Page
          </Typography>
          <Intro />
          <Button
            id="start_comparing_button"
            variant="contained"
            color="primary"
            onClick={() => {
              setShowIntro(false);
            }}
          >
            Start Comparing Contents
          </Button>
        </div>
      </div>
    );
  }

  // just loading settings
  if (state === null || state === undefined) {
    return (
      <ExpertSettings setStateExternal={setState} />
    );
  }

  return (
    <div className={classes.root} id="id_expert_rating_page">
      {/* For Selenium to know when the page is loaded */}
      {pending || state === null || state === undefined ? (
        <div id="id_pending_expert" />
      ) : (
        <div id="id_no_pending_expert" />
      )}

      {!isIdValid(videoA) || !isIdValid(videoB) ||
       !isIdValid(videoIdA) || !isIdValid(videoIdB) ? (
         <div id="id_pending_expert_video" />
        ) : (
          <div id="id_no_pending_expert_video" />
        )}

      {submitPending ? (
        <div id="id_pending_submit" />
      ) : (
        <div id="id_no_pending_submit" />
      )}

      {commentsOpen === 'left' && <SidePanel videoId={videoA} />}

      <div className={classes.centered}>
        <div className={classes.videoContainer}>
          <div id="video-left">
            <VideoSelector
              showControls={showControls}
              id={videoA}
              tourIndex={tourIndex === 1 ? -1 : tourIndex}
              setId={(x) => {
                setSubmitted(false);
                setComparison(getDefaultComparison());
                setVideoA(x);
                timerBegin();
                updateExistingRating(x, videoB);
              }}
              getNewId={() => loadVideo(setVideoA, 1)}
              openComments={() => {
                setCommentsOpen(commentsOpen === 'left' ? 'none' : 'left');
              }}
            />
            {videoAError !== null && videoAError !== undefined && (
              <Alert severity="error" id="id_left_error">
                {videoAError}
              </Alert>
            )}
          </div>
          <div id="video-right">
            <VideoSelector
              showControls={showControls}
              id={videoB}
              tourIndex={tourIndex === 1 ? 1 : -1}
              setId={(x) => {
                setSubmitted(false);
                setComparison(getDefaultComparison());
                setVideoB(x);
                timerBegin();
                updateExistingRating(videoA, x);
              }}
              getNewId={() => loadVideo(setVideoB, 2)}
              openComments={() => {
                setCommentsOpen(commentsOpen === 'right' ? 'none' : 'right');
              }}
            />
            {videoBError !== null && videoBError !== undefined && (
              <Alert severity="error" id="id_right_error">
                {videoBError}
              </Alert>
            )}
          </div>
        </div>
        {videoA !== '' && videoB !== '' && (
          <>
            {featureList
              .filter((f) => state[`${f}_enabled`])
              .map((feature) => (
                <div
                  key={feature}
                  id={`id_container_feature_${feature}`}
                  className={classes.featuresContainer}
                >
                  <div className={classes.featureNameDisplay}>
                    <Grid container spacing={0}>
                      <Grid
                        item
                        xs={12}
                        direction="row"
                        justify="center"
                        alignItems="center"
                        container
                        style={{ height: '20px' }}
                      >
                        <div>
                          {/* FEATURE NAME */}
                          <Tooltip
                            title="Click to check our definition"
                            aria-label="feature explanation"
                            interactive
                            style={{ marginLeft: '8px' }}
                            placement="left"
                          >
                            <Typography>
                              <a
                                href={featureLinks[feature]}
                                id={`id_explanation_${feature}`}
                                target="_blank"
                                rel="noreferrer"
                              >
                                {featureNames[feature] || feature}
                              </a>

                              {weights[feature] !== 1 &&
                            state.rating_mode !== 'confidence' &&
                            (state.rating_mode !== 'skip' ||
                              weights[feature] !== 0)
                                ? `, weight: ${weights[feature]}x`
                                : ''}
                            </Typography>
                          </Tooltip>
                        </div>

                        {/* SKIP FEATURE */}
                        {(state.rating_mode === 'skip' || state.rating_mode === 'confidence') && (
                        <div>
                          <Tooltip title="Skip this feature" aria-label="add">
                            <Checkbox
                              id={`id_checkbox_skip_${feature}`}
                              disabled={submitted}
                              checked={skipState[feature]}
                              onChange={(e) => {
                                setSkipState({
                                  ...skipState,
                                  [feature]: e.target.checked,
                                });
                                setWeights({
                                  ...weights,
                                  [feature]: e.target.checked ? 0.0 : 1.0,
                                });

                                const newConfidenceState = e.target.checked ?
                                  0 : getDefaultConfidence()[feature];

                                setConfidenceState({
                                  ...confidenceState,
                                  [feature]: newConfidenceState,
                                });
                              }}
                              name={feature}
                              color="primary"
                            />
                          </Tooltip>
                        </div>
                        )}
                        {/* CONFIDENCE STARS */}
                        {state.rating_mode === 'confidence' && (
                          <div>
                            <Tooltip
                              title={
                                confidenceLabels[
                                  confidenceState[feature] !== 0 &&
                                  confidenceStateHover[feature] !== -1
                                    ? confidenceStateHover[feature]
                                    : confidenceState[feature]
                                ]
                              }
                              aria-label="add"
                            >
                              <Rating
                                id={`id_${feature}_confidence`}
                                name={`${feature}_confidence`}
                                max={nStars}
                                disabled={submitted}
                                value={confidenceState[feature]}
                                onChange={(event, newValue) => {
                                  let val = newValue;
                                  if (!val) {
                                    val = 0;
                                  }
                                  setConfidenceState({
                                    ...confidenceState,
                                    [feature]: val,
                                  });
                                  setWeights({
                                    ...weights,
                                    [feature]: val * STARS_TO_WEIGHT_COEFF,
                                  });

                                  setSkipState({ ...skipState, [feature]: val === 0 });
                                }}
                                onChangeActive={(event, newHover) => {
                                  setConfidenceStateHover({
                                    ...confidenceStateHover,
                                    [feature]: newHover,
                                  });
                                }}
                              />
                            </Tooltip>
                          </div>
                        )}
                      </Grid>
                    </Grid>
                  </div>
                  <div className={classes.sliderContainer}>
                    <IconButton
                      aria-label="left"
                      onClick={() => {
                        setComparison({ ...comparison, [feature]: 0 });
                      }}
                      style={{ color: 'black', transform: 'rotate(180deg)' }}
                      disabled={
                        submitted ||
                        (state.rating_mode === 'skip' && skipState[feature]) ||
                        weights[feature] === 0
                      }
                    >
                      <DoubleArrowIcon />
                    </IconButton>
                    <TutorialTooltip
                      open={
                        (tourIndex === 2 && feature === 'reliability') ||
                        (tourIndex === 3 && feature === 'engaging')
                      }
                      tourIndex={tourIndex}
                    >
                      <Slider
                        ValueLabelComponent={ValueLabelComponent}
                        id={`slider_expert_${feature}`}
                        aria-label="custom thumb label"
                        color="secondary"
                        value={comparison[feature]}
                        className={classes.slider}
                        track={false}
                        disabled={
                          submitted ||
                          (state.rating_mode === 'skip' &&
                            skipState[feature]) ||
                          weights[feature] === 0
                        }
                        onChange={(e, value) => {
                          const newComparison = {
                            ...comparison,
                            [feature]: value,
                          };
                          if (onSliderFeatureChanged) {
                            onSliderFeatureChanged(feature, value);
                          }
                          setComparison(newComparison);
                          registerSliderChange(newComparison);
                        }}
                      />
                    </TutorialTooltip>

                    <IconButton
                      aria-label="right"
                      onClick={() => {
                        setComparison({ ...comparison, [feature]: 100 });
                      }}
                      style={{ color: 'black' }}
                      disabled={
                        submitted ||
                        (state.rating_mode === 'skip' && skipState[feature]) ||
                        weights[feature] === 0
                      }
                    >
                      <DoubleArrowIcon />
                    </IconButton>
                  </div>
                </div>
              ))}
            <div className={classes.featuresContainer}>
              {submitted && (
                <div id="id_submitted_text_info">
                  <Typography>
                    Change one of the video to submit a new comparison
                  </Typography>
                </div>
              )}
              <TutorialTooltip i={4} tourIndex={tourIndex}>
                <Button
                  variant="contained"
                  color="primary"
                  size="large"
                  id="expert_submit_btn"
                  onClick={
                    submitted ? () => setSubmitted(false) : submitComparison
                  }
                >
                  {getSubmitButtonName()}
                </Button>
              </TutorialTooltip>
              {error && (
                <Alert
                  variant="outlined"
                  id="id_expert_submit_error"
                  severity="error"
                >
                  {error}
                </Alert>
              )}
              {commentError && (
              <Alert severity="warning" id="id_please_comment_alert">
                You have set a {nStars}-star confidence on one of the features.
                Please comment one of the videos to explain the reason for it before
                submitting the rating.
              </Alert>
              )}
            </div>
            {showControls && (
            <>
              <Button
                variant="contained"
                color="secondary"
                onClick={() => {
                  setShowIntro(true);
                }}
                size="small"
              >
                <InfoIcon /> Help
              </Button>
              <Button
                style={{ marginLeft: 8 }}
                variant="contained"
                color="secondary"
                onClick={() => setTourIndex(0)}
                size="small"
              >
                <InfoIcon /> Start Tour
              </Button>
              <Button
                variant="contained"
                color="secondary"
                id="id_rating_settings"
                onClick={() => {
                  setFormOpen(true);
                }}
                size="small"
              >
                <SettingsIcon /> Settings
              </Button>
            </>)}
          </>
        )}
      </div>
      {commentsOpen === 'right' && <SidePanel videoId={videoB} />}

      <Dialog
        open={formOpen}
        onClose={closeForm}
        scroll="body"
        aria-describedby="scroll-dialog-description"
      >
        <DialogContent>
          <DialogContentText
            id="scroll-dialog-description"
            ref={descriptionElementRef}
            tabIndex={-1}
          >
            <ExpertSettings setStateExternal={setState} />
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button
            onClick={closeForm}
            id="id_close_settings_form"
            color="primary"
          >
            Close
          </Button>
        </DialogActions>
      </Dialog>
      {tourIndex >= 0 && (
        <div
          style={{
            position: 'fixed',
            bottom: '10px',
            right: '10px',
            background: '#ccc',
            border: '1px solid black',
          }}
        >
          <Button
            onClick={() => setTourIndex(-1)}
            variant="contained"
            style={{ backgroundColor: 'red', margin: 8 }}
          >
            Close tips
          </Button>
          {tourIndex + 1 < 8 && (
            <Button
              onClick={() => setTourIndex(tourIndex + 1)}
              variant="contained"
              color="primary"
              style={{ margin: 8 }}
            >
              Next tip
            </Button>
          )}
        </div>
      )}
    </div>
  );
};
