// variables starting with underscore can be unused
/* eslint no-unused-vars: ["error", { "argsIgnorePattern": "^_" }] */

import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import Button from '@material-ui/core/Button';
import { useParams, useHistory } from 'react-router-dom';
import Alert from '@material-ui/lab/Alert';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';
import VideoCard from './VideoCard';

import { TournesolAPI } from '../api';
import { minNumRateLater } from '../constants';
import VideoSelector from './ExpertInterface/VideoSelector';

const useStyles = makeStyles(() => ({
  topVideos: {
    textAlign: 'center',
    display: 'flex',
    alignItems: 'center',
    flexDirection: 'column',

    justifyContent: 'center' },
  titleContainer: {
    margin: '4px',
    padding: '4px',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'space-around',
    flex: '0 0 auto',
  },
  alignItemsAndJustifyContent: {
    flexDirection: 'column',
    width: '100%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },

}));

export default () => {
  const { videoIdAdd = null } = useParams();
  const [submitStatus, setSubmitStatus] = React.useState(null);
  const [submitResult, setSubmitResult] = React.useState(null);
  const [requestStatus, setRequestStatus] = React.useState(null);
  const [rateLater, setRateLater] = React.useState([]);
  const [count, setCount] = React.useState(null);
  const [offset, setOffset] = React.useState(0);
  const [topVideo, setTopVideo] = React.useState(null);
  const [topVideoId, setTopVideoId] = React.useState('');
  const [topInRateLater, setTopInRateLater] = React.useState(null);
  const [needFirstFromURL, setNeedFirstFromURL] = React.useState(true);
  const classes = useStyles();
  const history = useHistory();

  if (videoIdAdd !== null && needFirstFromURL) {
    setNeedFirstFromURL(false);
    setTopVideoId(videoIdAdd);
  }

  const getInformation = (vId) => {
    if (topVideo === null || topVideo === undefined || topVideo.video_id !== vId) {
      const api = new TournesolAPI.VideosApi();
      api.videosList({ videoId: vId }, (err, data) => {
        if (!err && data.count === 1) {
          setTopVideo(data.results[0]);
        } else {
          setTopVideo(undefined);
        }
      });
    }
  };

  const sampleTopVideo = () => {
    const api = new TournesolAPI.ExpertRatingsApi();
    api.expertRatingsSamplePopularVideoRetrieve({ noRateLater: true },
      (err, data) => {
        if (!err) {
          setTopVideo(data);
          setTopVideoId(data.video_id);
        }
      });
  };

  const limit = 5;

  const loadRateLater = () => {
    const api = new TournesolAPI.RateLaterApi();
    api.rateLaterList({ limit, offset }, (err, data) => {
      if (!err) {
        setRateLater(data.results);
        setCount(data.count);
        setRequestStatus(true);
      }
    });
  };

  const addToRateLater = (vid) => {
    setSubmitStatus(undefined);
    const api = new TournesolAPI.RateLaterApi();
    api.rateLaterCreate({ video: vid }, (err, _data) => {
      if (err) {
        setSubmitResult(false);
      } else {
        setSubmitResult(true);
        setRequestStatus(null);
      }
      setSubmitStatus(true);
    });
  };

  if (videoIdAdd !== null && submitStatus === null) {
    setSubmitStatus(undefined);
    const api = new TournesolAPI.RateLaterApi();
    api.rateLaterCreate({ video: videoIdAdd }, (err, _data) => {
      if (err) {
        setSubmitResult(false);
      } else {
        setSubmitResult(true);
      }
      setSubmitStatus(true);
    });
  }

  if (requestStatus === null && (videoIdAdd === null || submitStatus === true)) {
    setRequestStatus(undefined);
    loadRateLater();
  }

  const onRateLaterClick = () => {
    setRequestStatus(undefined);
    loadRateLater();
  };

  return (
    <>
      <div className={classes.topVideos} id="id_ratelater_page_all">
        <span style={{ fontSize: '300%' }}>Add videos to your rate-later list</span><br />
        <span>Copy-paste the URL of a favorite video
          of yours to add it to import on Tournesol.<br />
          You can search them in your{' '}
          <a href="https://www.youtube.com/feed/history">
            YouTube history page
          </a>, or your{' '}
          <a href="https://www.youtube.com/playlist?list=LL">
            liked video playlist
          </a>.<br />
          You can also let us load the most viewed videos on our platform.<br />
          Our{' '}
          <a href="https://chrome.google.com/webstore/detail/tournesol-extension/nidimbejmadpggdgooppinedbggeacla?hl=en">
            Google chrome extension
          </a> can also help you import videos effortlessly.<br />
          You will then be able to rate the videos you imported.

        </span>
        <br />

        {topVideo !== null && topVideo !== undefined && (
        <div id="id_top_video_videocard">
          <VideoCard
            video={topVideo === undefined ? null : topVideo}
            onRateLaterClick={onRateLaterClick}
            setInRateLater={setTopInRateLater}
            showRateLater={false}
          />
        </div>
        )}
      </div>

      {/* {requestStatus !== true && <p>Loading...</p>} */}

      <Grid
        container
        direction="row"
        justify="center"
        alignItems="center"
      >
        <Grid item>
          <VideoSelector
            id={topVideoId}
            setId={(v) => {
              setTopVideoId(v);
              getInformation(v);
              setSubmitStatus(undefined);
            }}
            getNewId={() => {
              sampleTopVideo();
              setSubmitStatus(undefined);
            }}
            showPlayer={false}
            showCommentButton={false}
            showReport={false}
          />
        </Grid>

        {topInRateLater !== true && topVideoId !== null && topVideoId !== undefined
      && topVideoId !== '' && (videoIdAdd === null || topVideoId !== videoIdAdd) && (
      <Grid item>
        <Button
          size="large"
          variant="contained"
          color="primary"
          id="id_big_add_rate_later"
          onClick={() => {
            addToRateLater(topVideoId);
            setTopVideoId('');
            setTopVideo(undefined);
          }}
        >
          Add to my rate later list!
        </Button>
      </Grid>
        )}

        {submitStatus === true && submitResult === true && (
        <Grid item>
          <Alert severity="success" id="id_rate_later_submit_ok">
            Video added to your Rate Later list
          </Alert>
        </Grid>
        )}

        {submitStatus === true && submitResult === false && (
        <Grid item>

          <Alert severity="warning" id="id_rate_later_submit_already_exists">
            Video was already in your Rate Later list
          </Alert>
        </Grid>
        )}
      </Grid>

      <div
        className={classes.alignItemsAndJustifyContent}
        style={{ paddingTop: '20px' }}
      >
        {(count !== null && count >= minNumRateLater) && (

        <Button
          size="large"
          variant="contained"
          color="secondary"
          id="id_big_expert_interface"
          onClick={() => {
            history.push('/rate');
          }}
        >
          Rate content
        </Button>

        )}
        {count !== null && count < minNumRateLater && (
          <Alert severity="info" id="id_recommend_add_more">
            We recommend that you add {minNumRateLater - count} more videos before
            moving to content rating.
          </Alert>
        )}
      </div>

      <div
        style={{ paddingTop: '20px' }}
      >

        {(requestStatus === true || (count !== null && count > 0)) && (
        <div className={classes.alignItemsAndJustifyContent}>
          <div
            style={{ paddingTop: '20px' }}
            className={classes.alignItemsAndJustifyContent}
          >

            <Typography variant="h4" gutterBottom>
              Your rate-later list now has {count} videos
            </Typography>

            <div style={{ flexDirection: 'row' }}>

              {count > 0 && (
              <div id="id_controls_prev_next">
                <Button
                  disabled={offset <= 0}
                  variant="contained"
                  color="primary"
                  id="id_rate_later_prev"
                  onClick={() => {
                    setOffset(Math.max(offset - limit, 0));
                    setRequestStatus(null);
                  }}
                >
                  Previous {limit}
                </Button>
                &nbsp;
                Showing videos {offset + 1} to {Math.min(count, offset + limit + 1)}
                &nbsp;
                <Button
                  disabled={offset + limit >= count}
                  variant="contained"
                  color="primary"
                  id="id_rate_later_next"
                  onClick={() => {
                    setOffset(Math.min(count, offset + limit));
                    setRequestStatus(null);
                  }}
                >
                  Next {limit}
                </Button>
              </div>
              )}
            </div>
          </div>
          <div
            className="class_rate_later_list"
            style={{ paddingTop: '20px' }}
          >
            {rateLater
              .map((v) => (
                <VideoCard video={v.video_info} showPlayer_ showChart_ />
              ))}
          </div>
        </div>
        )}

      </div>
    </>
  );
};
