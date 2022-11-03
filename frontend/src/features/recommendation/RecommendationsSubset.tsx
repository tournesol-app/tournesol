import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Button, Grid, Stack } from '@mui/material';

import EntityCard from 'src/components/entity/EntityCard';
import { useCurrentPoll } from 'src/hooks';
import { Recommendation } from 'src/services/openapi';
import { getRecommendations } from 'src/utils/api/recommendations';

interface RecommendationsSubsetProps {
  nbr?: number;
  displayControls?: boolean;
}

const RecommendationsSubset = ({
  nbr = 4,
  displayControls = false,
}: RecommendationsSubsetProps) => {
  const { t } = useTranslation();
  const { criterias, name: pollName } = useCurrentPoll();

  const [entities, setEntities] = useState<Array<Recommendation>>([]);

  useEffect(() => {
    const getRecommendationsAsync = async () => {
      const recommendations = await getRecommendations(
        pollName,
        nbr,
        '',
        criterias
      );
      setEntities(recommendations.results ?? []);
    };

    getRecommendationsAsync();
  }, [criterias, nbr, pollName]);

  return (
    <Box>
      {displayControls && (
        <Box mb={2}>
          <Stack direction="row" justifyContent="center" spacing={2}>
            <Button variant="contained" disableElevation>
              {t('recommendationsSubset.bestOfLastMonth')}
            </Button>
            <Button variant="contained" disableElevation>
              {t('recommendationsSubset.bestOfAllTime')}
            </Button>
          </Stack>
        </Box>
      )}
      <Grid container gap={2} flexDirection="column">
        {entities.map((entity) => (
          <Grid item key={entity.uid}>
            <EntityCard
              entity={entity}
              compact={false}
              entityTypeConfig={{ video: { displayPlayer: false } }}
            />
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default RecommendationsSubset;
