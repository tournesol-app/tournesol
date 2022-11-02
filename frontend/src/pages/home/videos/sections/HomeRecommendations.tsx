import React, { useEffect, useState } from 'react';

import { Grid } from '@mui/material';

import EntityCard from 'src/components/entity/EntityCard';
import { useCurrentPoll } from 'src/hooks';
import { Recommendation } from 'src/services/openapi';
import { getRecommendations } from 'src/utils/api/recommendations';

/**
 * TODO: make this component generic:
 * - rename HomeRecommendations -> RecommendationsExtract
 * - make the limit configurable
 * - make the offset configurable
 */
const HomeRecommendations = () => {
  const { criterias, name: pollName } = useCurrentPoll();

  const [entities, setEntities] = useState<Array<Recommendation>>([]);

  useEffect(() => {
    const getRecommendationsAsync = async () => {
      const recommendations = await getRecommendations(
        pollName,
        4,
        '',
        criterias
      );
      setEntities(recommendations.results ?? []);
    };

    getRecommendationsAsync();
  }, [criterias, pollName]);

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

export default HomeRecommendations;
