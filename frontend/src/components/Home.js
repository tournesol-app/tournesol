import React from 'react';

import { makeStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import Alert from '@material-ui/lab/Alert';
import Grid from '@material-ui/core/Grid';
import Button from '@material-ui/core/Button';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import YouTube from 'react-youtube';
import AlertTitle from '@material-ui/lab/AlertTitle';
import { useHistory, Link } from 'react-router-dom';
import { TournesolAPI } from '../api';
import EmailAddVerifyAlert from './EmailAddVerifyAlert';
import { minNumRateLater } from '../constants';

const youtubeOpts = {
  height: '275px',
  width: '490px',
  playerVars: {
    // https://developers.google.com/youtube/player_parameters
    autoplay: 0,
    controls: 0,
    iv_load_policy: 0,
    modestbranding: 1,
    // playsinline: 1,
    showinfo: 0,
    rel: 0,
  },
};

const LinkOrText = ({ text, link, isLink = false }) => {
  if (isLink) {
    return (
      <Link to={link}>
        {text}
      </Link>
    );
  }

  return (
    <span>
      {text}
    </span>
  );
};

const useStyles = makeStyles(() => ({
  root: {
    width: '100%',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    minWidth: '420px',
  },
  imageContainer: {
    width: '100%',
    maxWidth: '700px',
    position: 'relative',
    color: 'black',
  },
  descriptionContainer: {
    width: '100%',
    maxWidth: '900px',
    position: 'relative',
    textAlign: 'center',
  },
  statistic: {
    fontSize: 70,
  },
  spacing: {
    minHeight: '30px',
  },
  arrowCon: {
    width: '100%',
  },
  arrowMedia: {
    minHeight: '100px',
    width: '100%',
    objectFit: 'cover',
  },
  arrowText: {
    position: 'absolute',
    color: 'black',
    transform: 'translateX(-50%)',
  },
}));

export default () => {
  const classes = useStyles();
  const history = useHistory();
  const [data, setData] = React.useState({});
  const [loading, setLoading] = React.useState(true);
  const [numRatedLater, setNumRatedLater] = React.useState(null);
  const [numRatings, setNumRatings] = React.useState(null);

  const showArrowTutorial = (window.is_authenticated === 0) || (numRatings === 0);

  // obtaining number of ratings
  if (numRatings === null) {
    setNumRatings(undefined);
    const api = new TournesolAPI.ExpertRatingsApi();
    api.expertRatingsList({ limit: 1 }, (err, dataNum) => {
      if (!err) {
        setNumRatings(dataNum.count);
      } else {
        setNumRatings(0);
      }
    });
  }

  if (numRatedLater === null) {
    setNumRatedLater(undefined);
    const api = new TournesolAPI.RateLaterApi();
    api.rateLaterList({ limit: 1 }, (err, dataNum) => {
      if (!err) {
        setNumRatedLater(dataNum.count);
      } else {
        setNumRatedLater(0);
      }
    });
  }

  if (loading) {
    /// request statistics from the server
    const api = new TournesolAPI.StatisticsApi();
    api.view((_err, statsData) => {
      setData(statsData);
      setLoading(false);
    });
  }

  // get one statistic from data or "..." if loading
  const getStatistic = (key) => (loading ? '...' : data[key].toLocaleString());

  const showExpertLink = (numRatedLater !== null && numRatedLater !== undefined &&
                  numRatedLater >= minNumRateLater);

  return (
    <div className={classes.root}>

      <Grid
        container
        direction="row"
        justify="center"
        alignItems="center"
      >
        <Grid item xs={6}>
          <Typography variant="h3">
            Tournesol{' '}
            <span role="img" aria-label="tournesol">
              <img
                style={{ width: '1em', marginTop: '0.3em' }}
                src="/static/tournesol_logo.png"
                alt="tournesol"
              />
            </span>
          </Typography>
          <Typography paragraph>
            Tournesol aims to identify top videos of public utility
            by eliciting contributors' judgements on content quality.
            <br />
            Please also consider using our{' '}
            <a href="https://chrome.google.com/webstore/detail/tournesol-extension/nidimbejmadpggdgooppinedbggeacla?hl=en">
              Chrome extension
            </a>, our{' '}
            <a href="https://addons.mozilla.org/en-US/firefox/addon/tournesol-extension/">
              Firefox extension
            </a>,
            and our{' '}
            <a href="https://play.google.com/store/apps/details?id=com.tournesolapp&hl=en&gl=US">
              Android application
            </a>.
            <br />
            Find out more with our{' '}
            <a href="http://wiki.tournesol.app/">
              wiki
            </a>,
            check out our{' '}
            <a href="https://github.com/tournesol-app/tournesol">
              open-source code
            </a>, join our{' '}
            <a href="https://discord.gg/3KApy6tHAM">
              Discord
            </a>,
            and{' '}
            <a href="/tournesol.public.latest.csv.zip" id="id_public_database_download">
              download our public database
            </a>.
          </Typography>

          {window.is_authenticated ? (
            <div style={{ textAlign: 'center', width: '95%' }}>
              <EmailAddVerifyAlert />
              {(numRatedLater !== null && numRatedLater !== undefined) && (
              <Button
                id={showExpertLink ? 'id_home_toexpert' : 'id_home_toratelater'}
                variant="contained"
                color="secondary"
                size="large"
                onClick={() => history.push(showExpertLink ? '/rate/' : '/rate_later')}
                style={{ minWidth: '50%', minHeight: '60px', fontSize: '150%' }}
              >
                <span role="img" aria-label="tournesol">
                  <img
                    style={{ width: '1em', marginTop: '0.3em' }}
                    src="/static/tournesol_logo.png"
                    alt="tournesol"
                  />
                </span>
                Contribute
                <span role="img" aria-label="tournesol">
                  <img
                    style={{ width: '1em', marginTop: '0.3em' }}
                    src="/static/tournesol_logo.png"
                    alt="tournesol"
                  />
                </span>
                <div className={classes.spacing} />
              </Button>
              )}
            </div>
          ) : (
            <div style={{ textAlign: 'center' }}>
              <Typography variant="h5">We need your contributions!</Typography>
              <Typography variant="span">Please log in or sign up to contribute
                to Tournesol's mission:
              </Typography>
              <div className={classes.spacing} />
              <Typography paragraph>
                <Button
                  variant="contained"
                  color="primary"
                  size="large"
                  href="/login/google-oauth2/"
                >
                  Log in with&nbsp;
                  <FontAwesomeIcon icon={['fab', 'google']} />
                </Button>{' '}
                <Button
                  variant="contained"
                  color="primary"
                  size="large"
                  onClick={() => history.push('/login')}
                  id="login_button"
                >
                  Log in
                </Button>{' '}
                <Button
                  variant="contained"
                  color="secondary"
                  size="large"
                  onClick={() => history.push('/signup')}
                  id="signup_button"
                >
                  Sign up
                </Button>
                <div className={classes.spacing} />
              </Typography>
            </div>
          )}
        </Grid>

        <Grid item xs={6}>
          {window.ENABLE_YOUTUBE_VIDEO_EMBED === 1 ? (
            <YouTube key="xSqqXN0D4fY" videoId="xSqqXN0D4fY" opts={youtubeOpts} />
          ) : <span>Youtube xSqqXN0D4fY</span>}
        </Grid>

      </Grid>

      <div className={classes.spacing} />

      <div className={classes.descriptionContainer}>

        <div style={{ display: 'flex', justifyContent: 'center' }}>
          <Alert
            severity="warning"
            icon={false}
            variant="outlined"
            style={{ width: '450px' }}
          >
            <AlertTitle>Tournesol is still under construction</AlertTitle>
            Please{' '}
            <a href="mailto:le-nguyen.hoang@science4all.org">contact us</a> if
            you identify bugs or potential improvements.

          </Alert>
        </div>

        <div style={{ display: 'flex', justifyContent: 'center' }}>
          <Alert
            severity="info"
            icon={false}
            variant="outlined"
            style={{ width: '450px' }}
          >
            <AlertTitle>We are currently experiencing issues with email validation</AlertTitle>
            You may fail to be delivered the email we send you to confirm your email address.
            Please try again later.
            Our team is doing its best to fix this issue as soon as possible.
            We thank you for your patience and understanding, and we apologize
            for the inconvenience.

          </Alert>
        </div>

        <div className={classes.spacing} />

        {showArrowTutorial === true && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <div className={classes.arrowCon}>
              <div style={{ position: 'relative' }}>
                <img
                  aria-label="arrow-tutorial"
                  className={classes.arrowMedia}
                  src="/static/home_arrow_no_text_transparent.png"
                />
                <div
                  className={classes.arrowText}
                  style={{
                    left: '6.05%',
                    top: '51.4%',
                  }}
                >
                  <LinkOrText
                    link="/signup"
                    text="Create"
                    isLink={window.is_authenticated === 0}
                  />
                  {' '}
                  an account
                  <br />
                  Validate your email<br />
                  <LinkOrText
                    link="/login"
                    text="Log in"
                    isLink={window.is_authenticated === 0}
                  />
                  {' '}
                  to your account
                </div>
                <div
                  className={classes.arrowText}
                  style={{
                    left: '49.48%',
                    top: '72.12%',
                    transform: 'translate(-50%, -100%)',
                  }}
                >
                  Add the best videos<br />
                  you have watched<br />
                  to the{' '}"
                  <LinkOrText
                    link="/rate_later"
                    text="rate-later"
                    isLink={window.is_authenticated === 1}
                  />
                  " list
                </div>
                <div
                  className={classes.arrowText}
                  style={{
                    left: '77.18%',
                    top: '43.52%',
                  }}
                >
                  <LinkOrText
                    link="/rate"
                    text="Compare videos"
                    isLink={window.is_authenticated === 1}
                  />
                  {' '}of<br />
                  your "rate-later" list
                </div>
              </div>
            </div>
          </Grid>
        </Grid>)}

        <div className={classes.spacing} />

        <Typography variant="h4">
          Our journey so far encompasses...
        </Typography>

        <Grid container spacing={3} style={{ justifyContent: 'center' }}>
          <Grid item xs={12} sm={6} md={4}>
            <h1 className={classes.statistic}>
              {getStatistic('total_experts')}
            </h1>
            <Typography paragraph>contributors</Typography>
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <h1 className={classes.statistic}>
              {getStatistic('certified_experts')}
            </h1>
            <Typography paragraph>
              contributors certified by their institutional e-mail addresses
            </Typography>
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <h1 className={classes.statistic}>
              {getStatistic('n_sum_comparisons')}
            </h1>
            <Typography paragraph>
              comparison-based ratings between pairs of video contents on
              all quality features
            </Typography>
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <h1 className={classes.statistic}>{getStatistic('n_rated_videos')}</h1>
            <Typography paragraph>video contents from YouTube</Typography>
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <h1 className={classes.statistic}>{getStatistic('weekly_active_ratings')}</h1>
            <Typography paragraph>new comparisons this week</Typography>
          </Grid>
        </Grid>

        <Typography paragraph style={{ marginTop: 16 }}>
          By using this website you agree to our{' '}
          <a href="/privacy_policy">
            Privacy policy
          </a>
        </Typography>
      </div>
    </div>
  );
};
