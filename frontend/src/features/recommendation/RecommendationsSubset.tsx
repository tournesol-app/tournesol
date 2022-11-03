import React, { useEffect, useState } from 'react';

import { Grid } from '@mui/material';

import EntityCard from 'src/components/entity/EntityCard';
import { useCurrentPoll } from 'src/hooks';
import { Recommendation } from 'src/services/openapi';
import { getRecommendations } from 'src/utils/api/recommendations';

interface RecommendationsSubsetProps {
  nbr?: number;
}

/**
 * TODO: make this component generic:
 * - rename HomeRecommendations -> RecommendationsExtract
 * - make the limit configurable
 * - make the offset configurable
 */
const RecommendationsSubset = ({ nbr = 4 }: RecommendationsSubsetProps) => {
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
  );
};

export default RecommendationsSubset;
