import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router';

import { CircularProgress } from '@material-ui/core';

import type { PaginatedVideoList } from 'src/services/openapi';
import VideoList from '../videos/VideoList';
import SearchFilter from './SearchFilter';
import { getRecommendedVideos } from './RecommendationApi';

function VideoRecommendationFromFilters() {
  const prov: PaginatedVideoList = { count: 0, results: [] };
  const [videos, setVideos] = useState(prov);
  const [isLoading, setIsLoading] = useState(true);
  const searchParams = useLocation().search;

  useEffect(() => {
    setIsLoading(true);
    getRecommendedVideos(searchParams, (videos: PaginatedVideoList) => {
      setVideos(videos);
      setIsLoading(false);
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams]);

  return (
    <div className="main">
      <SearchFilter />
      {isLoading ? <CircularProgress /> : <VideoList videos={videos} />}
    </div>
  );
}
export default VideoRecommendationFromFilters;
