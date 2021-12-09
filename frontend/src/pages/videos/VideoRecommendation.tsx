import React, { useState, useEffect } from 'react';
import { useLocation, useHistory } from 'react-router-dom';

import { Box } from '@material-ui/core';

import type { PaginatedVideoSerializerWithCriteriaList } from 'src/services/openapi';
import Pagination from 'src/components/Pagination';
import VideoList from 'src/features/videos/VideoList';
import SearchFilter from 'src/features/recommendation/SearchFilter';
import { getRecommendedVideos } from 'src/features/recommendation/RecommendationApi';
import { ContentBox } from 'src/components';
import LoaderWrapper from 'src/components/LoaderWrapper';

function VideoRecommendationPage() {
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
    document.querySelector('main')?.scrollTo({ top: 0 });
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
    <ContentBox noMinPadding maxWidth="lg">
      <Box px={{ xs: 2, sm: 0 }}>
        <SearchFilter />
      </Box>
      <LoaderWrapper isLoading={isLoading}>
        <VideoList
          videos={videos.results || []}
          emptyMessage={
            isLoading ? '' : 'No video corresponds to your search criterias.'
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
  );
}

export default VideoRecommendationPage;
