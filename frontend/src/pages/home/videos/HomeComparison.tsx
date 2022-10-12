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
import { Recommendation } from 'src/services/openapi';
import { getUserComparisonsRaw } from 'src/utils/api/comparisons';
import { getEntityName } from 'src/utils/constants';
import { setPendingRating } from 'src/utils/comparison/pending';
import { alreadyComparedWith, selectRandomEntity } from 'src/utils/entity';
import { getTutorialVideos } from 'src/utils/polls/videos';

interface Props {
  enablePendingComparison?: boolean;
}

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
const HomeComparison = ({ enablePendingComparison = false }: Props) => {
  const { t } = useTranslation();

  const { criterias, options, name: pollName } = useCurrentPoll();
  const tutorialLength = options?.tutorialLength ?? 4;

  const { isLoggedIn } = useLoginState();
  const [tutoRedirect, setTutoRedirect] = useState(true);

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

  const entityName = getEntityName(t, pollName);

  /**
   * This effect determines if the user should be redirected to the tutorial
   * when clicking on the submit button, and selects the two videos of the
   * comparison.
   *
   * These videos are selected from the pool returned by `getTutorialVideos`
   * to keep the home page comparison in sync with the tutorial.
   */
  useEffect(() => {
    async function getAlternativesAsync(
      getAlts: () => Promise<Array<Recommendation>>
    ) {
      const alts = await getAlts();

      if (alts.length > 0) {
        return alts;
      }
      return [];
    }

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
    const alternativesPromise = getAlternativesAsync(getTutorialVideos);

    Promise.all([comparisonsPromise, alternativesPromise])
      .then(([comparisons, entities]) => {
        // Deterine if the user should be redirected to the tutorial.
        let shouldBeRedirected = true;
        if (isLoggedIn && comparisons[0] >= tutorialLength) {
          shouldBeRedirected = false;
        }
        setTutoRedirect(shouldBeRedirected);

        // Build the comparison.
        if (entities.length > 0) {
          const entityA = selectRandomEntity(entities, []);
          let alreadyComparedWithA: string[] = [];

          // Exlude entities already compared with A.
          if (isLoggedIn) {
            alreadyComparedWithA = alreadyComparedWith(
              entityA.uid,
              comparisons[1]
            );
          }

          const entityB = selectRandomEntity(
            entities,
            alreadyComparedWithA.concat([entityA.uid])
          );
          setComparison([entityA.uid, entityB.uid]);
          setSelectorA({ uid: entityA.uid, rating: null });
          setSelectorB({ uid: entityB.uid, rating: null });
        }
        if (isLoading) {
          setIsLoading(false);
        }
      })
      .catch(() => {
        if (isLoading) {
          setIsLoading(false);
        }

        setApiError(true);
      });

    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isLoggedIn, pollName, tutorialLength]);

  const handleSliderChange = (criterion: string, value: number | undefined) => {
    if (value) {
      setCriteriaValue(value);

      if (enablePendingComparison) {
        setPendingRating(pollName, uidA, uidB, criterion, value);
      }
    }
  };

  return (
    <Grid
      container
      sx={{
        gap: '8px',
      }}
    >
      <Grid
        item
        xs
        component={Card}
        sx={{
          alignSelf: 'start',
        }}
      >
        <EntitySelector
          title={`${entityName} 1`}
          value={selectorA}
          onChange={setSelectorA}
          otherUid={uidB}
          light
        />
      </Grid>
      <Grid
        item
        xs
        component={Card}
        sx={{
          alignSelf: 'start',
        }}
      >
        <EntitySelector
          title={`${entityName} 2`}
          value={selectorB}
          onChange={setSelectorB}
          otherUid={uidA}
          light
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
                to={
                  tutoRedirect
                    ? `/comparison/?series=true&keep_uids_after_redirect=true&uidA=${uidA}&uidB=${uidB}`
                    : `/comparison/?uidA=${uidA}&uidB=${uidB}`
                }
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
