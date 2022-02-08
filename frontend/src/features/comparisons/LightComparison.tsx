import React, { useState, useEffect } from 'react';
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

import { useNotifications } from 'src/hooks';
import { ComparisonRequest, UsersService } from 'src/services/openapi';
import ComparisonSliders from 'src/features/comparisons/ComparisonSliders';
import { getRecommendedVideos } from 'src/features/recommendation/RecommendationApi';
import { VideoCardFromId } from 'src/features/videos/VideoCard';

const useStyles = makeStyles((theme: Theme) => ({
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

// XXX should be move somewhere
function getRandomInt(min: number, max: number): number {
  min = Math.ceil(min);
  max = Math.floor(max);
  return Math.floor(Math.random() * (max - min)) + min;
}

/**
 * A light comparison UI.
 *
 * This comparison UI is intended to be used by both anonymous and logged
 * users. For now, only comparisons for logged users are supported.
 *
 * Contrary to the standard comparison UI, it only displays two videos without
 * extraneous control. Users can't select videos, nor to set the comparison
 * public.
 */
const LightComparison = () => {
  const classes = useStyles();

  const { t } = useTranslation();
  const { showSuccessAlert } = useNotifications();

  const [isLoading, setIsLoading] = useState(true);
  const [initialComparison, setInitialComparison] =
    useState<ComparisonRequest | null>(null);

  const [videoIdA, setVideoIdA] = useState('');
  const [videoIdB, setVideoIdB] = useState('');

  /**
   * Get an array of two random and distinct video IDs from the Tournesol
   * recommendations.
   *
   * The recommendations can be narrowed using the `searchString` parameter.
   * If less than two video IDs are found, the rest of the array is filled
   * with empty strings.
   *
   * @param searchString a string used by the request's URLSearchParams
   */
  const getRecommendations = async (searchString: string) => {
    let idA = '';
    let idB = '';

    const response = await getRecommendedVideos(searchString);

    const count = response && response.count ? response.count : 0;
    const max =
      response && response.results && response.results.length > 0
        ? response.results.length
        : 0;

    if (count >= 2 && response.results) {
      const randA = getRandomInt(0, max);
      let randB = getRandomInt(0, max);

      while (randA === randB) {
        randB = getRandomInt(0, max);
      }

      idA = response.results[randA]['video_id'];
      idB = response.results[randB]['video_id'];
    } else if (count === 1 && response.results) {
      idA = response.results[0]['video_id'];
    }

    return [idA, idB];
  };

  const getUserComparison = (idA: string, idB: string) => {
    UsersService.usersMeComparisonsRetrieve({
      videoIdA: idA,
      videoIdB: idB,
    })
      .then((comparison) => {
        setInitialComparison(comparison);
      })
      .catch((err) => {
        console.error(err);
        setInitialComparison(null);
      });
  };

  useEffect(() => {
    const process = async () => {
      const empty = (elem: string) => elem === '' || !elem;

      // randomly pick two recent videos
      const recent = await getRecommendations('?date=Month');
      const displayedVideos = [...recent];

      // use all time recommendations if the recent videos < 2
      if (displayedVideos.some(empty)) {
        const allTime = await getRecommendations('');

        if (displayedVideos[0] === '') {
          displayedVideos[0] = allTime[0];
        }

        if (displayedVideos[1] === '') {
          displayedVideos[1] = allTime[1];
        }
      }

      setVideoIdA(displayedVideos[0]);
      setVideoIdB(displayedVideos[1]);
      getUserComparison(displayedVideos[0], displayedVideos[1]);
      setIsLoading(false);
    };

    process();
  }, []);

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
    }

    showSuccessAlert(t('comparison.successfullySubmitted'));
  };

  return (
    <Grid container className={classes.content}>
      <Grid item xs component={Card} className={classes.card}>
        <Box m={0.5}>
          <Typography variant="h5" className={classes.cardTitle}>
            Video 1
          </Typography>
        </Box>
        <VideoCardFromId videoId={videoIdA} compact />
      </Grid>
      <Grid item xs component={Card} className={classes.card}>
        <Box m={0.5}>
          <Typography variant="h5" className={classes.cardTitle}>
            Video 2
          </Typography>
        </Box>
        <VideoCardFromId videoId={videoIdB} compact />
      </Grid>
      <Grid
        item
        xs={12}
        className={classes.centering}
        style={{ marginTop: '16px' }}
      >
        {videoIdA && videoIdB ? (
          isLoading ? (
            <CircularProgress />
          ) : (
            <ComparisonSliders
              submit={onSubmitComparison}
              initialComparison={initialComparison}
              videoA={videoIdA}
              videoB={videoIdB}
              enableOptional={false}
              isComparisonPublic={false}
            />
          )
        ) : (
          <Typography paragraph>
            {t('lightComparison.notEnoughVideos')}
          </Typography>
        )}
      </Grid>
    </Grid>
  );
};

export default LightComparison;
