import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Button, Grid, Stack, useTheme } from '@mui/material';

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
  const theme = useTheme();

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
            <Button
              variant="outlined"
              disableElevation
              // TODO: see how we can add this to the theme palette
              sx={{
                color: '#fff',
                borderColor: '#fff',
                '&:hover': { color: theme.palette.primary.main },
              }}
            >
              {t('recommendationsSubset.bestOfLastMonth')}
            </Button>
            <Button
              variant="outlined"
              disableElevation
              // TODO: see how we can add this to the theme palette
              sx={{
                color: '#fff',
                borderColor: '#fff',
                '&:hover': { color: theme.palette.primary.main },
              }}
            >
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
