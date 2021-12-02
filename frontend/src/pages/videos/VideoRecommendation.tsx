import React, { useState, useEffect } from 'react';
import { useLocation, useHistory } from 'react-router-dom';

import { CircularProgress, Box } from '@material-ui/core';

import type { PaginatedVideoSerializerWithCriteriaList } from 'src/services/openapi';
import Pagination from 'src/components/Pagination';
import VideoList from 'src/features/videos/VideoList';
import SearchFilter from 'src/features/recommendation/SearchFilter';
import { getRecommendedVideos } from 'src/features/recommendation/RecommendationApi';
import { ContentBox } from 'src/components';

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
    searchParams.delete('offset');
    searchParams.append('offset', newOffset.toString());
    history.push('/recommendations/?' + searchParams.toString());
  }

  useEffect(() => {
    setIsLoading(true);
    getRecommendedVideos(
      location.search,
      (videos: PaginatedVideoSerializerWithCriteriaList) => {
        setVideos(videos);
        setIsLoading(false);
      }
    );
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location.search]);

  return (
    <ContentBox noMinPadding>
      <Box px={{ xs: 2, sm: 0 }}>
        <SearchFilter />
      </Box>
      {isLoading ? (
        <CircularProgress />
      ) : (
        <VideoList videos={videos.results || []} />
      )}
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
