import React, { useState, useEffect } from 'react';
import { useLocation, useHistory } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Box } from '@mui/material';

import type { PaginatedVideoSerializerWithCriteriaList } from 'src/services/openapi';
import Pagination from 'src/components/Pagination';
import VideoList from 'src/features/videos/VideoList';
import SearchFilter from 'src/features/recommendation/SearchFilter';
import { getRecommendedVideos } from 'src/features/recommendation/RecommendationApi';
import { ContentBox, ContentHeader } from 'src/components';
import LoaderWrapper from 'src/components/LoaderWrapper';
import { scrollToTop } from 'src/utils/ui';

function VideoRecommendationPage() {
  const { t } = useTranslation();
  const prov: PaginatedVideoSerializerWithCriteriaList = {
    count: 0,
    results: [],
  };
  const [videos, setVideos] = useState(prov);
  const [isLoading, setIsLoading] = useState(true);
  const location = useLocation();
  const history = useHistory();
  const searchParams = new URLSearchParams(location.search);
  const limit = 20;
  const offset = Number(searchParams.get('offset') || 0);
  const videoCount = videos.count || 0;

  function handleOffsetChange(newOffset: number) {
    searchParams.set('offset', newOffset.toString());
    history.push({ search: searchParams.toString() });
    scrollToTop();
  }

  useEffect(() => {
    const fetchVideos = async () => {
      setIsLoading(true);
      setVideos(await getRecommendedVideos(location.search));
      setIsLoading(false);
    };
    fetchVideos();
  }, [location.search]);

  return (
    <>
      <ContentHeader title={t('recommendationsPage.title')} />
      <ContentBox noMinPaddingX maxWidth="lg">
        <Box px={{ xs: 2, sm: 0 }}>
          <SearchFilter />
        </Box>
        <LoaderWrapper isLoading={isLoading}>
          <VideoList
            videos={videos.results || []}
            emptyMessage={
              isLoading ? '' : t('noVideoCorrespondsToSearchCriterias')
            }
          />
        </LoaderWrapper>
        {!isLoading && videoCount > 0 && (
          <Pagination
            offset={offset}
            count={videoCount}
            onOffsetChange={handleOffsetChange}
            limit={limit}
          />
        )}
      </ContentBox>
    </>
  );
}

export default VideoRecommendationPage;
