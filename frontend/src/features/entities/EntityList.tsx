import React from 'react';

import VideoList from 'src/features/videos/VideoList';
import { useCurrentPoll } from 'src/hooks';
import { Recommendation } from 'src/services/openapi/models/Recommendation';
import { YOUTUBE_POLL_NAME } from 'src/utils/constants';
import {
  videoFromRelatedEntity,
  videoWithScoresFromRecommendation,
} from 'src/utils/entity';
import { ActionList, RelatedEntityObject, VideoObject } from 'src/utils/types';

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
 *       +-- CandidateList
 *       +-- VideoList
 *       +-- etc.
 */
function EntityList({
  entities,
  actions,
  settings = [],
  personalScores,
  emptyMessage,
}: Props) {
  const { name: pollName } = useCurrentPoll();

  const fromEntitiesToVideos = (
    entities: RelatedEntityObject[] | Recommendation[] | undefined
  ): VideoObject[] => {
    if (!entities) {
      return [];
    }
    return entities.map((entity) => {
      if ('tournesol_score' in entity) {
        return videoWithScoresFromRecommendation(entity);
      }

      return videoFromRelatedEntity(entity);
    });
  };

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

  return <></>;
}

export default EntityList;
