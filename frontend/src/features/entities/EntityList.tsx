import React, { useState, useEffect } from 'react';
import { Box, Typography } from '@mui/material';

import EntityCard from 'src/components/entity/EntityCard';
import { useCurrentPoll, useLoginState } from 'src/hooks';
import { Recommendation } from 'src/services/openapi/models/Recommendation';
import { ActionList, RelatedEntityObject } from 'src/utils/types';
import { idFromUid } from 'src/utils/video';

interface Props {
  entities: RelatedEntityObject[] | Recommendation[] | undefined;
  actions?: ActionList;
  settings?: ActionList;
  emptyMessage?: React.ReactNode;
  personalScores?: { [uid: string]: number };
}

const AvailableEntity = ({
  children,
  uid,
}: {
  children: React.ReactNode;
  uid: string;
}) => {
  const [isAvailableOnYoutube, setIsAvailableOnYoutube] = useState(false);

  useEffect(() => {
    const img = new Image();
    img.src = `https://i.ytimg.com/vi/${idFromUid(uid)}/mqdefault.jpg`;
    img.onload = function () {
      setIsAvailableOnYoutube(img.width !== 120);
    };
  }, [uid]);

  return isAvailableOnYoutube ? <>{children}</> : null;
};

/**
 * Display a list of entities.
 *
 * Entities can be pure entities, or entities expanded with data related to
 * the current poll, like the number of comparisons, the tournesol score,
 * etc.
 *
 * According to the current poll, this component renders a specific child
 * component able to correctly display the entities.
 */
function EntityList({
  entities,
  actions,
  settings = [],
  // personalScores,
  emptyMessage,
}: Props) {
  const { isLoggedIn } = useLoginState();
  const { options } = useCurrentPoll();

  const defaultEntityActions = isLoggedIn
    ? options?.defaultAuthEntityActions
    : options?.defaultAnonEntityActions;

  return (
    <>
      {entities && entities.length ? (
        entities.map((entity: Recommendation | RelatedEntityObject) => (
          <AvailableEntity key={entity.uid} uid={entity.uid}>
            <Box mx={1} my={2}>
              <EntityCard
                entity={entity}
                actions={actions ?? defaultEntityActions}
                settings={settings}
                compact={false}
                entityTypeConfig={{ video: { displayPlayer: false } }}
              />
            </Box>
          </AvailableEntity>
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
