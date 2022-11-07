import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Grid, Typography, useTheme } from '@mui/material';

import { LoaderWrapper } from 'src/components';
import EntityCard from 'src/components/entity/EntityCard';
import { useCurrentPoll } from 'src/hooks';
import { Recommendation } from 'src/services/openapi';
import { getRecommendations } from 'src/utils/api/recommendations';
import RecommendationsSubsetControls from './RecommendationsSubsetControls';

interface RecommendationsSubsetProps {
  // the maximum number of entity to display
  nbr?: number;
  // if true display few buttons allowing to filter the recommendations
  displayControls?: boolean;
  // the color of the control buttons
  controlsColor?: string;
}

const RecommendationsSubset = ({
  nbr = 4,
  displayControls = false,
  controlsColor = '#fff',
}: RecommendationsSubsetProps) => {
  const theme = useTheme();

  const { t } = useTranslation();
  const { criterias, name: pollName } = useCurrentPoll();

  const [isLoading, setIsLoading] = useState(true);

  const [recoDate, setRecoDate] = useState('Month');
  const [entities, setEntities] = useState<Array<Recommendation>>([]);

  useEffect(() => {
    const searchParams = new URLSearchParams();
    searchParams.append('date', recoDate);

    const getRecommendationsAsync = async () => {
      setIsLoading(true);

      const recommendations = await getRecommendations(
        pollName,
        nbr,
        searchParams.toString(),
        criterias
      );

      setIsLoading(false);
      setEntities(recommendations.results ?? []);
    };

    getRecommendationsAsync();
  }, [criterias, nbr, pollName, recoDate]);

  const dateControlChangeCallback = (value: string) => {
    setRecoDate(value ?? '');
  };

  return (
    <Box>
      {displayControls && (
        <Box mb={2}>
          <RecommendationsSubsetControls
            controlsColor={controlsColor}
            selectedDate={recoDate}
            dateControlChangeCallback={dateControlChangeCallback}
          />
        </Box>
      )}
      <LoaderWrapper isLoading={isLoading}>
        {entities.length === 0 ? (
          <Typography paragraph textAlign="center">
            {t('recommendationsSubset.noRecommendationHasBeenFound')}
          </Typography>
        ) : (
          <Grid container gap={2} flexDirection="column">
            {entities.map((entity) => (
              <Grid
                item
                key={entity.uid}
                // Allow the RecommendationsSubset's parent to overwrite the
                // text color without impacting the EntityCard.
                sx={{ color: theme.palette.text.primary }}
              >
                <EntityCard
                  entity={entity}
                  compact={false}
                  entityTypeConfig={{ video: { displayPlayer: false } }}
                  sxNoBorder
                />
              </Grid>
            ))}
          </Grid>
        )}
      </LoaderWrapper>
    </Box>
  );
};

export default RecommendationsSubset;
