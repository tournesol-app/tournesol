import React from 'react';
import { Box, Typography } from '@mui/material';
import EntityCard from 'src/components/entity/EntityCard';

import { Recommendation } from 'src/services/openapi/models/Recommendation';
import { ActionList, RelatedEntityObject } from 'src/utils/types';

interface Props {
  entities: RelatedEntityObject[] | Recommendation[] | undefined;
  actions?: ActionList;
  settings?: ActionList;
  emptyMessage?: React.ReactNode;
  personalScores?: { [uid: string]: number };
}

/**
 * Display a list of entities.
 *
 * Entities can be pure entities, or entities expanded with data related to
 * the current poll, like the number of comparisons, the tournesol score,
 * etc.
 *
 * According to the current poll, this component renders a specific child
 * component able to correctly display the entities.
 *
 * Component tree:
 *
 *   ParentPage
 *   |
 *   +-- EntityList (here)
 *       |
 *       +-- VideoList
 *       +-- generic entity list
 */
function EntityList({
  entities,
  actions,
  settings = [],
  // personalScores,
  emptyMessage,
}: Props) {
  {
    /*
  if (pollName === YOUTUBE_POLL_NAME) {
    return (
      <VideoList
        videos={fromEntitiesToVideos(entities)}
        actions={actions}
        settings={settings}
        personalScores={personalScores}
        emptyMessage={emptyMessage}
      />
    );
  }
  */
  }

  return (
    <>
      {entities && entities.length ? (
        entities.map((entity: Recommendation | RelatedEntityObject) => (
          <Box key={entity.uid} mx={1} my={2}>
            <EntityCard
              entity={entity}
              actions={actions}
              settings={settings}
              compact={false}
            />
          </Box>
        ))
      ) : (
        <Box m={2}>
          <Typography variant="h5" component="h2" align="center">
            {emptyMessage}
          </Typography>
        </Box>
      )}
    </>
  );
}

export default EntityList;
