import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useHistory, useLocation } from 'react-router-dom';

import { Box, IconButton } from '@mui/material';
import { Search } from '@mui/icons-material';

import {
  ContentBox,
  ContentHeader,
  LoaderWrapper,
  Pagination,
  PreferencesIconButtonLink,
} from 'src/components';
import { useCurrentPoll } from 'src/hooks';
import EntityList from 'src/features/entities/EntityList';
import { PaginatedRecommendationList } from 'src/services/openapi';
import { getRecommendations } from 'src/utils/api/recommendations';
import { getFeedTopItemsPageName } from 'src/utils/constants';

const ENTITIES_LIMIT = 20;

const FeedTopItems = () => {
  const { t } = useTranslation();

  const history = useHistory();
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const offset = Number(searchParams.get('offset') || 0);

  const { name: pollName, criterias, options } = useCurrentPoll();

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
    const searchString = new URLSearchParams();
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
  }, [criterias, offset, options, pollName]);

  return (
    <>
      <ContentHeader title={getFeedTopItemsPageName(t, pollName)} />
      <ContentBox noMinPaddingX maxWidth="lg">
        <Box
          px={{ xs: 2, sm: 0 }}
          mb={1}
          display="flex"
          justifyContent="flex-end"
          columnGap={2}
        >
          {/* Create a component similar to PreferencesIconButtonLink */}
          <IconButton color="secondary" disabled>
            <Search />
          </IconButton>
          <PreferencesIconButtonLink hash={`#${pollName}-feed-top`} />
        </Box>
        <LoaderWrapper isLoading={isLoading}>
          <EntityList
            entities={entities.results}
            emptyMessage={isLoading ? '' : t('entityList.noItems')}
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

export default FeedTopItems;
