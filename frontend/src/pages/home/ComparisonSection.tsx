import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

import { CircularProgress, Button, Grid, Card } from '@mui/material';

import EntitySelector, {
  SelectorValue,
} from 'src/features/entity_selector/EntitySelector';
import { getEntityName } from 'src/utils/constants';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import CriteriaSlider from 'src/features/comparisons/CriteriaSlider';

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

  const fetchWeeklyComparison = () => {
    if (isLoading) {
      setIsLoading(false);
    }
    // TODO This must return two video ids of the weekly comparison
    // TODO If the two weekly videos have already been compared, change one of them
    // using the same method as Auto function
    return ['yt:vqDbMEdLiCs', 'yt:1PGm8LslEb4'];
  };

  const [uidA, uidB] = fetchWeeklyComparison();

  const [selectorA, setSelectorA] = useState<SelectorValue>({
    uid: uidA,
    rating: null,
  });
  const [selectorB, setSelectorB] = useState<SelectorValue>({
    uid: uidB,
    rating: null,
  });

  const entityName = getEntityName(t, pollName);

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
