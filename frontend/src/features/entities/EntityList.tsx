import React from 'react';

import VideoList from 'src/features/videos/VideoList';
import { useCurrentPoll } from 'src/hooks';
import { Video, VideoSerializerWithCriteria } from 'src/services/openapi';
import { Recommendation } from 'src/services/openapi/models/Recommendation';
import { YOUTUBE_POLL_NAME } from 'src/utils/constants';
import {
  videoFromRelatedEntity,
  videoWithCriteriaFromRecommendation,
} from 'src/utils/entity';
import { ActionList, RelatedEntityObject, VideoObject } from 'src/utils/types';

interface Props {
  entities: RelatedEntityObject[] | Recommendation[] | undefined;
  isRecommendation: boolean;
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
  isRecommendation,
  actions,
  settings = [],
  personalScores,
  emptyMessage,
}: Props) {
  const { name: pollName } = useCurrentPoll();

  const fromEntitiesToVideos = (
    entities: RelatedEntityObject[] | Recommendation[] | undefined,
    isRecommendation: boolean
  ): VideoObject[] => {
    if (isRecommendation) {
      return _getResultsAsVideoWithCriteria(entities as Recommendation[]);
    }
    return _getResultsAsVideo(entities);
  };

  /**
   * Return Video[] from RelatedEntityObject[]
   */
  const _getResultsAsVideo = (
    results: RelatedEntityObject[] | undefined
  ): Video[] => {
    if (!results) {
      return [];
    }
    return results.map((entity) => videoFromRelatedEntity(entity));
  };

  /**
   * Return VideoSerializerWithCriteria[] from Recommendation[]
   */
  const _getResultsAsVideoWithCriteria = (
    results: Recommendation[] | undefined
  ): VideoSerializerWithCriteria[] => {
    if (!results) {
      return [];
    }
    return results.map((entity) => videoWithCriteriaFromRecommendation(entity));
  };

  if (pollName === YOUTUBE_POLL_NAME) {
    return (
      <VideoList
        videos={fromEntitiesToVideos(entities, isRecommendation)}
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
