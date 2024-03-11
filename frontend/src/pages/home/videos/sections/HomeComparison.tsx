import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

import {
  CircularProgress,
  Button,
  Grid,
  Card,
  Alert,
  Box,
} from '@mui/material';

import EntitySelector, {
  SelectorValue,
} from 'src/features/entity_selector/EntitySelector';
import CriteriaSlider from 'src/features/comparisons/CriteriaSlider';
import { useLoginState, useCurrentPoll } from 'src/hooks';
import { getUserComparisonsRaw } from 'src/utils/api/comparisons';
import { setPendingRating } from 'src/utils/comparison/pending';
import { alreadyComparedWith, selectRandomEntity } from 'src/utils/entity';
import { getTutorialVideos } from 'src/utils/polls/videos';

/**
 * The Home Comparison.
 *
 * Contains two videos and a single slider, and a button inviting to submit
 * the comparison. The button redirects to the comparison interface.
 *
 * The videos are selected from the pool provided by `getTutorialVideos`. To
 * modify this behaviour consider passing `getTutorialVideos` as a prop to
 * this component.
 */
const HomeComparison = () => {
  const { t } = useTranslation();

  const { criterias, options, name: pollName } = useCurrentPoll();
  const tutorialLength = options?.tutorialLength ?? 4;

  const { isLoggedIn } = useLoginState();

  const [isLoading, setIsLoading] = useState(true);
  const [apiError, setApiError] = useState(false);
  const [criteriaValue, setCriteriaValue] = useState(0);

  const [comparison, setComparison] = useState<[string, string]>(['', '']);
  const uidA = comparison[0];
  const uidB = comparison[1];

  const [selectorA, setSelectorA] = useState<SelectorValue>({
    uid: uidA,
    rating: null,
  });
  const [selectorB, setSelectorB] = useState<SelectorValue>({
    uid: uidB,
    rating: null,
  });

  /**
   * This effect determines if the user should be redirected to the tutorial
   * when clicking on the submit button, and selects the two videos of the
   * comparison.
   *
   * These videos are selected from the pool returned by `getTutorialVideos`
   * to keep the home page comparison in sync with the tutorial.
   */
  useEffect(() => {
    async function getUserComparisonsAsync(
      loggedIn: boolean,
      pName: string
    ): Promise<[number, string[]]> {
      if (!loggedIn) {
        return [0, []];
      }

      const paginatedComparisons = await getUserComparisonsRaw(pName, 100);
      let results: string[] = [];

      if (paginatedComparisons.results) {
        results = paginatedComparisons.results.map(
          (comp) => comp.entity_a.uid + '/' + comp.entity_b.uid
        );
      }

      return [paginatedComparisons.count || 0, results];
    }

    const comparisonsPromise = getUserComparisonsAsync(isLoggedIn, pollName);
    const alternativesPromise = getTutorialVideos();

    Promise.all([comparisonsPromise, alternativesPromise])
      .then(([comparisons, entities]) => {
        // Build the comparison.
        if (entities.length > 0) {
          const recoA = selectRandomEntity(entities, []);
          let alreadyComparedWithA: string[] = [];

          // Exlude entities already compared with A.
          if (isLoggedIn) {
            alreadyComparedWithA = alreadyComparedWith(
              recoA.entity.uid,
              comparisons[1]
            );
          }

          const recoB = selectRandomEntity(
            entities,
            alreadyComparedWithA.concat([recoA.entity.uid])
          );
          setComparison([recoA.entity.uid, recoB.entity.uid]);
          setSelectorA({ uid: recoA.entity.uid, rating: null });
          setSelectorB({ uid: recoB.entity.uid, rating: null });
        }

        setIsLoading(false);
      })
      .catch(() => {
        setIsLoading(false);
        setApiError(true);
      });
  }, [isLoggedIn, pollName, tutorialLength]);

  const handleSliderChange = (criterion: string, value: number | undefined) => {
    if (value != null) {
      setCriteriaValue(value);
      setPendingRating(pollName, uidA, uidB, criterion, value);
    }
  };

  return (
    <Grid
      container
      sx={{
        gap: '8px',
      }}
    >
      <Grid item xs display="flex" flexDirection="column" alignSelf="stretch">
        <EntitySelector
          variant="noControl"
          value={selectorA}
          onChange={setSelectorA}
          otherUid={uidB}
        />
      </Grid>
      <Grid item xs display="flex" flexDirection="column" alignSelf="stretch">
        <EntitySelector
          variant="noControl"
          value={selectorB}
          onChange={setSelectorB}
          otherUid={uidA}
        />
      </Grid>
      <Grid item xs={12} mt={1} component={Card} elevation={2}>
        {!isLoading ? (
          apiError ? (
            <Alert severity="warning" variant="filled" sx={{ width: '100%' }}>
              {t('homeComparison.sorryTheComparisonIsTemporarilyUnavailable')}
            </Alert>
          ) : (
            <Box
              width="100%"
              py={2}
              px={4}
              display="flex"
              alignItems="center"
              flexDirection="column"
            >
              <CriteriaSlider
                criteria={criterias[0].name}
                criteriaLabel={criterias[0].label}
                criteriaValue={criteriaValue}
                handleSliderChange={handleSliderChange}
              />
              <Button
                variant="contained"
                color="primary"
                size="large"
                component={Link}
                to={`/comparison?uidA=${uidA}&uidB=${uidB}`}
              >
                {t('homeComparison.compareTheVideos')}
              </Button>
            </Box>
          )
        ) : (
          <Box
            py={2}
            px={4}
            display="flex"
            alignItems="center"
            flexDirection="column"
          >
            <CircularProgress />
          </Box>
        )}
      </Grid>
    </Grid>
  );
};

export default HomeComparison;
