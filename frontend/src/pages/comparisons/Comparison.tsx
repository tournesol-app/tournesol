import React, { useState, useEffect, useRef } from 'react';
import { useHistory, useLocation } from 'react-router-dom';

import { makeStyles } from '@material-ui/core/styles';
import CircularProgress from '@material-ui/core/CircularProgress';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';

import { UsersService, Comparison } from 'src/services/openapi';
import { ensureVideoExistsOrCreate } from 'src/utils/video';
import ComparisonSliders from 'src/features/comparisons/Comparison';
import VideoSelector, {
  VideoSelectorHandle,
} from 'src/features/video_selector/VideoSelector';
import { showSuccessAlert } from 'src/utils/notifications';
import { useSnackbar } from 'notistack';
import { ContentHeader } from 'src/components';

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
  const classes = useStyles();
  const history = useHistory();
  const location = useLocation();
  const [isLoading, setIsLoading] = useState(true);
  const [initialComparison, setInitialComparison] = useState<Comparison | null>(
    null
  );
  const { enqueueSnackbar } = useSnackbar();

  const searchParams = new URLSearchParams(location.search);
  const videoA: string = searchParams.get('videoA') || '';
  const videoB: string = searchParams.get('videoB') || '';
  const selectorARef = useRef<VideoSelectorHandle>();
  const selectorBRef = useRef<VideoSelectorHandle>();

  const setVideo = (videoKey: string) => (videoId: string | null) => {
    searchParams.delete(videoKey);
    if (videoId) searchParams.append(videoKey, videoId);
    history.push('?' + searchParams.toString());
  };
  const [setVideoA, setVideoB] = [setVideo('videoA'), setVideo('videoB')];

  useEffect(() => {
    setIsLoading(true);
    setInitialComparison(null);
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
    if (videoA) await ensureVideoExistsOrCreate(videoA);
    if (videoB) await ensureVideoExistsOrCreate(videoB);
    if (initialComparison) {
      const { video_a, video_b, criteria_scores, duration_ms } = c;
      await UsersService.usersMeComparisonsUpdate(
        video_a.video_id,
        video_b.video_id,
        { criteria_scores, duration_ms }
      );
    } else {
      await UsersService.usersMeComparisonsCreate(c);
      setInitialComparison(c);
      selectorARef.current?.updateRating();
      selectorBRef.current?.updateRating();
    }
    showSuccessAlert(
      enqueueSnackbar,
      'The comparison has been succesfully submitted.'
    );
  };

  return (
    <>
      <ContentHeader title="Submit a comparison" />
      <div className={`${classes.root} ${classes.centering}`}>
        <Grid container className={classes.content} spacing={1}>
          <Grid item xs={6}>
            <Typography variant="h5">Video 1</Typography>
            <VideoSelector
              ref={selectorARef}
              videoId={videoA}
              setId={setVideoA}
              otherVideo={videoB}
            />
          </Grid>
          <Grid item xs={6}>
            <Typography variant="h5">Video 2</Typography>
            <VideoSelector
              ref={selectorBRef}
              videoId={videoB}
              setId={setVideoB}
              otherVideo={videoA}
            />
          </Grid>
          <Grid
            item
            xs={12}
            className={classes.centering}
            style={{ marginTop: '36px' }}
          >
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
    </>
  );
};

export default ComparisonPage;
