import React, { useState, useEffect, useRef, useMemo } from 'react';
import { useLocation, useHistory } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Box } from '@mui/material';

import type {
  PaginatedRecommendationList,
  Recommendation,
} from 'src/services/openapi';
import Pagination from 'src/components/Pagination';
import VideoList from 'src/features/videos/VideoList';
import SearchFilter from 'src/features/recommendation/SearchFilter';
import { getRecommendedVideos } from 'src/features/recommendation/RecommendationApi';
import { ContentBox, ContentHeader } from 'src/components';
import LoaderWrapper from 'src/components/LoaderWrapper';
import {
  saveRecommendationsLanguages,
  loadRecommendationsLanguages,
  recommendationsLanguagesFromNavigator,
} from 'src/utils/recommendationsLanguages';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import { videoWithCriteriaFromRecommendation } from 'src/utils/entity';

function RecommendationsPage() {
  const { t } = useTranslation();

  const history = useHistory();
  const location = useLocation();
  const { criterias } = useCurrentPoll();
  const [isLoading, setIsLoading] = useState(true);

  const prov: PaginatedRecommendationList = {
    count: 0,
    results: [],
  };

  const [entities, setVideos] = useState(prov);
  const entitiesCount = entities.count || 0;

  const searchParams = useMemo(
    () => new URLSearchParams(location.search),
    [location.search]
  );
  const limit = 20;
  const offset = Number(searchParams.get('offset') || 0);

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

    if (searchParams.get('language') === null) {
      let loadedLanguages = loadRecommendationsLanguages();

      if (loadedLanguages === null) {
        loadedLanguages = recommendationsLanguagesFromNavigator();
        saveRecommendationsLanguages(loadedLanguages);
      }

      searchParams.set('language', loadedLanguages);
      history.replace({ search: searchParams.toString() });
      return;
    }

    const fetchVideos = async () => {
      setIsLoading(true);
      setVideos(
        (await getRecommendedVideos(limit, location.search, criterias)) || []
      );
      setIsLoading(false);
    };
    fetchVideos();
  }, [location.search, history, searchParams, criterias]);

  const getResultsAsVideos = (results: Recommendation[] | undefined) => {
    if (!results) {
      return [];
    }
    return results.map((entity) => videoWithCriteriaFromRecommendation(entity));
  };

  return (
    <>
      <ContentHeader title={t('recommendationsPage.title')} />
      <ContentBox noMinPaddingX maxWidth="lg">
        <Box px={{ xs: 2, sm: 0 }}>
          <SearchFilter />
        </Box>
        <LoaderWrapper isLoading={isLoading}>
          <VideoList
            videos={getResultsAsVideos(entities.results)}
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
