import React, { useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';
import { useHistory, useLocation } from 'react-router-dom';

import { Alert, Box, IconButton } from '@mui/material';
import { Search } from '@mui/icons-material';

import {
  ContentBox,
  ContentHeader,
  LoaderWrapper,
  Pagination,
} from 'src/components';
import PreferencesIconButtonLink from 'src/components/buttons/PreferencesIconButtonLink';
import EntityList from 'src/features/entities/EntityList';
import { selectSettings } from 'src/features/settings/userSettingsSlice';
import { useCurrentPoll } from 'src/hooks';
import { PaginatedRecommendationList } from 'src/services/openapi';
import { getRecommendations } from 'src/utils/api/recommendations';
import { getFiltersFeedForYou } from 'src/utils/userSettings';

const ENTITIES_LIMIT = 20;

const FeedForYou = () => {
  const { t } = useTranslation();

  const history = useHistory();
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const offset = Number(searchParams.get('offset') || 0);

  const { name: pollName, criterias, options } = useCurrentPoll();
  const userSettings = useSelector(selectSettings).settings;
  const userPreferences: URLSearchParams = useMemo(() => {
    return getFiltersFeedForYou(pollName, options, userSettings);
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
          <PreferencesIconButtonLink hash="#feed-foryou" />
        </Box>
        {!isLoading && entities.count === 0 && (
          <Box mb={1} px={{ xs: 2, sm: 0 }}>
            <Alert severity="info">
              {t('feedForYou.thisPageDisplaysItemsAccordingToYourFilters')}
            </Alert>
          </Box>
        )}
        <LoaderWrapper isLoading={isLoading}>
          <EntityList
            entities={entities.results}
            emptyMessage={isLoading ? '' : t('feedForYou.noItems')}
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
