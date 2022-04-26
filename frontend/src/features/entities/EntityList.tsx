import React from 'react';

import { useTranslation } from 'react-i18next';

import VideoList from 'src/features/videos/VideoList';
import { useCurrentPoll } from 'src/hooks';
import { VideoSerializerWithCriteria } from 'src/services/openapi';
import { Recommendation } from 'src/services/openapi/models/Recommendation';
import { YOUTUBE_POLL_NAME } from 'src/utils/constants';
import { videoWithCriteriaFromRecommendation } from 'src/utils/entity';
import { ActionList } from 'src/utils/types';

interface Props {
  // entities are only Recommendation[] for now but we should also allow
  // "pure" entities, without data related to the current poll
  entities: Recommendation[] | undefined;
  actions?: ActionList;
  settings?: ActionList;
  personalScores?: { [uid: string]: number };
  isLoading: boolean;
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
  isLoading,
}: Props) {
  const { t } = useTranslation();
  const { name: pollName } = useCurrentPoll();

  /**
   * Return VideoSerializerWithCriteria[] from Recommendation[]
   */
  const getResultsAsVideoWithCriteria = (
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
        videos={getResultsAsVideoWithCriteria(entities)}
        actions={actions}
        settings={settings}
        personalScores={personalScores}
        emptyMessage={isLoading ? '' : t('noVideoCorrespondsToSearchCriterias')}
      />
    );
  }

  return <></>;
}

export default EntityList;
