import React, { useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';
import { useHistory, useLocation } from 'react-router-dom';

import {
  ContentBox,
  ContentHeader,
  LoaderWrapper,
  Pagination,
} from 'src/components';
import EntityList from 'src/features/entities/EntityList';
import { selectSettings } from 'src/features/settings/userSettingsSlice';
import { useCurrentPoll } from 'src/hooks';
import { PaginatedRecommendationList } from 'src/services/openapi';
import { getRecommendations } from 'src/utils/api/recommendations';
import { getDefaultRecommendationsSearchParams } from 'src/utils/userSettings';

const ENTITIES_LIMIT = 20;

const FeedForYou = () => {
  const { t } = useTranslation();

  const history = useHistory();
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const offset = Number(searchParams.get('offset') || 0);

  const { name: pollName, criterias, options } = useCurrentPoll();
  const userSettings = useSelector(selectSettings).settings;
  const userPreferences: string = useMemo(() => {
    // todo: load the default values for the feed For You instead
    return getDefaultRecommendationsSearchParams(
      pollName,
      options,
      userSettings
    );
  }, [pollName, options, userSettings]);

  const [isLoading, setIsLoading] = useState(true);
  const [entities, setEntities] = useState<PaginatedRecommendationList>({
    count: 0,
    results: [],
  });

  const onOffsetChange = (newOffset: number) => {
    searchParams.set('offset', newOffset.toString());
    history.push({ search: searchParams.toString() });
  };

  useEffect(() => {
    const searchString = new URLSearchParams(userPreferences);
    searchString.append('offset', offset.toString());

    const fetchEntities = async () => {
      setIsLoading(true);

      try {
        const newEntities = await getRecommendations(
          pollName,
          ENTITIES_LIMIT,
          searchString.toString(),
          criterias,
          options
        );
        setEntities(newEntities);
      } catch {
        // todo: display a message
      } finally {
        setIsLoading(false);
      }
    };

    fetchEntities();
  }, [criterias, offset, options, pollName, userPreferences]);

  return (
    <>
      <ContentHeader title={t('feedForYou.forYou')} />
      <ContentBox noMinPaddingX maxWidth="lg">
        <LoaderWrapper isLoading={isLoading}>
          <EntityList
            entities={entities.results}
            emptyMessage={
              // todo: invite the users to change their settings
              isLoading ? '' : t('feedForYou.noItems')
            }
          />
        </LoaderWrapper>
        {!isLoading && (entities.count ?? 0) > 0 && (
          <Pagination
            offset={offset}
            count={entities.count ?? 0}
            onOffsetChange={onOffsetChange}
            limit={ENTITIES_LIMIT}
          />
        )}
      </ContentBox>
    </>
  );
};

export default FeedForYou;
