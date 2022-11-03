import React, { useEffect, useState } from 'react';

import { Box, Grid } from '@mui/material';

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
  const { criterias, name: pollName } = useCurrentPoll();

  const [recoDate, setRecoDate] = useState('Month');
  const [entities, setEntities] = useState<Array<Recommendation>>([]);

  useEffect(() => {
    const searchParams = new URLSearchParams();
    searchParams.append('date', recoDate);

    const getRecommendationsAsync = async () => {
      const recommendations = await getRecommendations(
        pollName,
        nbr,
        searchParams.toString(),
        criterias
      );
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
