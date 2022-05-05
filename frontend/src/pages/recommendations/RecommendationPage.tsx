import React, { useState, useEffect, useRef, useMemo } from 'react';
import { useLocation, useHistory } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Box } from '@mui/material';

import type { PaginatedRecommendationList } from 'src/services/openapi';
import LoaderWrapper from 'src/components/LoaderWrapper';
import Pagination from 'src/components/Pagination';
import EntityList from 'src/features/entities/EntityList';
import SearchFilter from 'src/features/recommendation/SearchFilter';
import { getRecommendations } from 'src/features/recommendation/RecommendationApi';
import { ContentBox, ContentHeader } from 'src/components';

import {
  saveRecommendationsLanguages,
  loadRecommendationsLanguages,
  recommendationsLanguagesFromNavigator,
} from 'src/utils/recommendationsLanguages';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import { getRecommendationPageName } from 'src/utils/constants';

function RecommendationsPage() {
  const { t } = useTranslation();

  const history = useHistory();
  const location = useLocation();
  const { name: pollName, criterias, options } = useCurrentPoll();
  const [isLoading, setIsLoading] = useState(true);

  const prov: PaginatedRecommendationList = {
    count: 0,
    results: [],
  };

  const [entities, setEntities] = useState(prov);
  const entitiesCount = entities.count || 0;

  const searchParams = useMemo(
    () => new URLSearchParams(location.search),
    [location.search]
  );
  const limit = 20;
  const offset = Number(searchParams.get('offset') || 0);
  const autoLanguageDiscovery = options?.defaultRecoLanguageDiscovery ?? false;

  const locationSearchRef = useRef<string>();

  function handleOffsetChange(newOffset: number) {
    searchParams.set('offset', newOffset.toString());
    history.push({ search: searchParams.toString() });
  }

  useEffect(() => {
    if (location.search === locationSearchRef.current) {
      // This ref is used as a precaution, to avoid triggering
      // this effect redundantly, eg if "history" has changed.
      return;
    }
    locationSearchRef.current = location.search;

    if (autoLanguageDiscovery && searchParams.get('language') === null) {
      let loadedLanguages = loadRecommendationsLanguages();

      if (loadedLanguages === null) {
        loadedLanguages = recommendationsLanguagesFromNavigator();
        saveRecommendationsLanguages(loadedLanguages);
      }

      searchParams.set('language', loadedLanguages);
      history.replace({ search: searchParams.toString() });
      return;
    }

    const fetchEntities = async () => {
      setIsLoading(true);
      setEntities(
        (await getRecommendations(
          pollName,
          limit,
          location.search,
          criterias
        )) || []
      );
      setIsLoading(false);
    };
    fetchEntities();
  }, [
    autoLanguageDiscovery,
    criterias,
    history,
    location.search,
    pollName,
    searchParams,
  ]);

  return (
    <>
      <ContentHeader title={getRecommendationPageName(t, pollName)} />
      <ContentBox noMinPaddingX maxWidth="lg">
        <Box px={{ xs: 2, sm: 0 }}>
          <SearchFilter />
        </Box>
        <LoaderWrapper isLoading={isLoading}>
          <EntityList
            entities={entities.results}
            emptyMessage={
              isLoading ? '' : t('noVideoCorrespondsToSearchCriterias')
            }
          />
        </LoaderWrapper>
        {!isLoading && entitiesCount > 0 && (
          <Pagination
            offset={offset}
            count={entitiesCount}
            onOffsetChange={handleOffsetChange}
            limit={limit}
          />
        )}
      </ContentBox>
    </>
  );
}

export default RecommendationsPage;
