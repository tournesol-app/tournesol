import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { useHistory, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

import makeStyles from '@mui/styles/makeStyles';
import {
  CircularProgress,
  Grid,
  Typography,
  Card,
  Box,
  Theme,
} from '@mui/material';

import { UsersService, ComparisonRequest } from 'src/services/openapi';
import ComparisonSliders from 'src/features/comparisons/Comparison';
import VideoSelector, {
  VideoSelectorValue,
} from 'src/features/video_selector/VideoSelector';
import { ContentHeader } from 'src/components';
import { useNotifications } from 'src/hooks';

const useStyles = makeStyles((theme: Theme) => ({
  root: {
    width: '100%',
    height: '100%',
  },
  centering: {
    display: 'flex',
    alignItems: 'center',
    flexDirection: 'column',
    paddingTop: 16,
  },
  content: {
    maxWidth: '880px',
    gap: '8px',
  },
  card: {
    alignSelf: 'start',
  },
  cardTitle: {
    color: theme.palette.text.secondary,
  },
}));

const ComparisonPage = () => {
  const { t } = useTranslation();
  const classes = useStyles();
  const history = useHistory();
  const location = useLocation();
  const [isLoading, setIsLoading] = useState(true);
  const [initialComparison, setInitialComparison] =
    useState<ComparisonRequest | null>(null);
  const { showSuccessAlert } = useNotifications();
  const searchParams = new URLSearchParams(location.search);
  const videoA: string = searchParams.get('videoA') || '';
  const videoB: string = searchParams.get('videoB') || '';
  const [selectorA, setSelectorA] = useState<VideoSelectorValue>({
    videoId: videoA,
    rating: null,
  });
  const [selectorB, setSelectorB] = useState<VideoSelectorValue>({
    videoId: videoB,
    rating: null,
  });
  const [submitted, setSubmitted] = useState(false);

  const onChange = useCallback(
    (videoKey: string) => (newValue: VideoSelectorValue) => {
      const searchParams = new URLSearchParams(location.search);
      const videoId = newValue.videoId;
      if (searchParams.get(videoKey) !== videoId) {
        searchParams.delete(videoKey);
        if (videoId) {
          searchParams.append(videoKey, videoId);
        }
        history.push('?' + searchParams.toString());
      }
      if (videoKey === 'videoA') {
        setSelectorA(newValue);
      } else if (videoKey === 'videoB') {
        setSelectorB(newValue);
      }
      setSubmitted(false);
    },
    [history, location.search]
  );
  const onChangeA = useMemo(() => onChange('videoA'), [onChange]);
  const onChangeB = useMemo(() => onChange('videoB'), [onChange]);

  useEffect(() => {
    setIsLoading(true);
    setInitialComparison(null);
    if (selectorA.videoId !== videoA) {
      setSelectorA({ videoId: videoA, rating: null });
    }
    if (selectorB.videoId !== videoB) {
      setSelectorB({ videoId: videoB, rating: null });
    }
    if (videoA && videoB)
      UsersService.usersMeComparisonsRetrieve({
        videoIdA: videoA,
        videoIdB: videoB,
      })
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

  const onSubmitComparison = async (c: ComparisonRequest) => {
    if (initialComparison) {
      const { video_a, video_b, criteria_scores, duration_ms } = c;
      await UsersService.usersMeComparisonsUpdate({
        videoIdA: video_a.video_id,
        videoIdB: video_b.video_id,
        requestBody: { criteria_scores, duration_ms },
      });
    } else {
      await UsersService.usersMeComparisonsCreate({ requestBody: c });
      setInitialComparison(c);
      // Refresh ratings statistics after the comparisons have been submitted
      setSubmitted(true);
    }
    showSuccessAlert(t('comparison.successfullySubmitted'));
  };

  return (
    <>
      <ContentHeader title={t('comparison.submitAComparison')} />
      <div className={`${classes.root} ${classes.centering}`}>
        <Grid container className={classes.content}>
          <Grid item xs component={Card} className={classes.card}>
            <Box m={0.5}>
              <Typography variant="h5" className={classes.cardTitle}>
                Video 1
              </Typography>
            </Box>
            <VideoSelector
              value={selectorA}
              onChange={onChangeA}
              otherVideo={videoB}
              submitted={submitted}
            />
          </Grid>
          <Grid item xs component={Card} className={classes.card}>
            <Box m={0.5}>
              <Typography variant="h5" className={classes.cardTitle}>
                Video 2
              </Typography>
            </Box>
            <VideoSelector
              value={selectorB}
              onChange={onChangeB}
              otherVideo={videoA}
              submitted={submitted}
            />
          </Grid>
          <Grid
            item
            xs={12}
            className={classes.centering}
            style={{ marginTop: '16px' }}
          >
            {selectorA.rating && selectorB.rating ? (
              isLoading ? (
                <CircularProgress />
              ) : (
                <ComparisonSliders
                  submit={onSubmitComparison}
                  initialComparison={initialComparison}
                  videoA={videoA}
                  videoB={videoB}
                  isComparisonPublic={
                    selectorA.rating.is_public && selectorB.rating.is_public
                  }
                />
              )
            ) : (
              <Typography paragraph>
                {t('comparison.pleaseSelectTwoVideos')}
              </Typography>
            )}
          </Grid>
        </Grid>
      </div>
    </>
  );
};

export default ComparisonPage;
