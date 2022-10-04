import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

import { CircularProgress, Button, Grid, Card } from '@mui/material';

import EntitySelector, {
  SelectorValue,
} from 'src/features/entity_selector/EntitySelector';
import CriteriaSlider from 'src/features/comparisons/CriteriaSlider';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import { Recommendation } from 'src/services/openapi';
import { getEntityName } from 'src/utils/constants';
import { getTutorialVideos } from 'src/utils/polls/videos';
import { selectRandomEntity } from 'src/utils/entity';

/**
 * The Comparison Section.
 *
 * Contains two videos and a single slider, and a button inviting to submit the
 * comparison. The button redirects to the comparison interface.
 */
const ComparisonSection = () => {
  const { t } = useTranslation();

  const { criterias, name: pollName } = useCurrentPoll();
  const [isLoading, setIsLoading] = useState(true);
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
   * Create a comparison in the same way they are created in the tutorial.
   */
  useEffect(() => {
    async function getAlternativesAsync(
      getAlts: () => Promise<Array<Recommendation>>
    ) {
      const alts = await getAlts();

      if (isLoading) {
        setIsLoading(false);
      }
      if (alts.length > 0) {
        return alts;
      }
      return [];
    }

    getAlternativesAsync(getTutorialVideos).then((videos) => {
      if (videos.length > 0) {
        const entityA = selectRandomEntity(videos, []);
        const entityB = selectRandomEntity(videos, [entityA.uid]);
        setComparison([entityA.uid, entityB.uid]);
        setSelectorA({ uid: entityA.uid, rating: null });
        setSelectorB({ uid: entityB.uid, rating: null });
      }
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <Grid
      container
      sx={{
        maxWidth: '880px',
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
      <Grid
        item
        xs={12}
        sx={{
          mt: 1,
          display: 'flex',
          alignItems: 'center',
          flexDirection: 'column',
          py: 2,
          px: 4,
        }}
        component={Card}
        elevation={2}
      >
        {selectorA.rating && selectorB.rating && !isLoading ? (
          <>
            <CriteriaSlider
              criteria={criterias[0].name}
              criteriaLabel={criterias[0].label}
              criteriaValue={criteriaValue}
              handleSliderChange={(_, value) => {
                if (value) setCriteriaValue(value);
              }}
            />
            <Button
              variant="contained"
              color="primary"
              size="large"
              component={Link}
              to={`/comparison/?uidA=${uidA}&uidB=${uidB}`}
            >
              Compare the videos
            </Button>
          </>
        ) : (
          <CircularProgress />
        )}
      </Grid>
    </Grid>
  );
};

export default ComparisonSection;
