import React, { useState, useEffect } from 'react';
import { useHistory, useLocation } from 'react-router-dom';

import { makeStyles } from '@material-ui/core/styles';
import CircularProgress from '@material-ui/core/CircularProgress';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';

import { UsersService, Comparison, OpenAPI } from 'src/services/openapi';
import { ensureVideoExistOrCreate } from 'src/utils/video';
import ComparisonSliders from 'src/features/comparisons/Comparison';
import VideoSelector from 'src/features/video_selector/VideoSelector';
import { selectLogin } from 'src/features/login/loginSlice';

import { useAppSelector } from '../../app/hooks';

const useStyles = makeStyles(() => ({
  root: {
    width: '100%',
    height: '100%',
  },
  centering: {
    display: 'flex',
    alignItems: 'center',
    flexDirection: 'column',
    paddingTop: 32,
  },
  content: {
    paddingBottom: 32,
    paddingTop: 32,
    width: '880px',
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
  alertTop: {
    marginBottom: '15px',
  },
}));

const ComparisonPage = () => {
  const token = useAppSelector(selectLogin);
  const classes = useStyles();
  const history = useHistory();
  const location = useLocation();
  const [isLoading, setIsLoading] = useState(true);
  const [initialComparison, setInitialComparison] = useState<Comparison | null>(
    null
  );

  const searchParams = new URLSearchParams(location.search);
  const videoA: string | null = searchParams.get('videoA');
  const videoB: string | null = searchParams.get('videoB');

  const setVideo = (videoKey: string) => (videoId: string | null) => {
    searchParams.delete(videoKey);
    if (videoId) searchParams.append(videoKey, videoId);
    history.push('?' + searchParams.toString());
  };
  const [setVideoA, setVideoB] = [setVideo('videoA'), setVideo('videoB')];

  useEffect(() => {
    setIsLoading(true);
    setInitialComparison(null);
    OpenAPI.TOKEN = token?.access_token ?? '';
    if (videoA && videoB)
      UsersService.usersMeComparisonsRetrieve(videoA, videoB)
        .then((comparison) => {
          setInitialComparison(comparison);
          setIsLoading(false);
        })
        .catch((err) => {
          console.error(err);
          setInitialComparison(null);
          setIsLoading(false);
        });

    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [videoA, videoB]);

  const onSubmitComparison = async (c: Comparison) => {
    if (videoA) await ensureVideoExistOrCreate(videoA);
    if (videoB) await ensureVideoExistOrCreate(videoB);
    if (initialComparison) {
      const { video_a, video_b, criteria_scores, duration_ms } = c;
      UsersService.usersMeComparisonsUpdate(
        video_a.video_id,
        video_b.video_id,
        { criteria_scores, duration_ms }
      );
    } else {
      UsersService.usersMeComparisonsCreate(c);
      setInitialComparison(c);
    }
  };

  return (
    <div className={`${classes.root} ${classes.centering}`}>
      <Grid container className={classes.content}>
        <Grid item xs={6}>
          <VideoSelector
            videoId={videoA}
            setId={setVideoA}
            otherVideo={videoB}
          />
        </Grid>
        <Grid item xs={6}>
          <VideoSelector
            videoId={videoB}
            setId={setVideoB}
            otherVideo={videoA}
          />
        </Grid>
        <Grid item xs={12} className={classes.centering}>
          {videoA && videoB ? (
            isLoading ? (
              <CircularProgress />
            ) : (
              <ComparisonSliders
                submit={onSubmitComparison}
                initialComparison={initialComparison}
                videoA={videoA}
                videoB={videoB}
              />
            )
          ) : (
            <Typography paragraph>
              Please, enter two URLs or IDs of Youtube videos to compare them.
            </Typography>
          )}
        </Grid>
      </Grid>
    </div>
  );
};

export default ComparisonPage;
