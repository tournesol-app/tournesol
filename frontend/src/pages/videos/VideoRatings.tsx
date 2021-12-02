import React, { useState, useEffect } from 'react';
import { useLocation, useHistory } from 'react-router-dom';

import { CircularProgress, Box } from '@material-ui/core';

import type {
  ContributorRating,
  PaginatedContributorRatingList,
} from 'src/services/openapi';
import Pagination from 'src/components/Pagination';
import VideoList from 'src/features/videos/VideoList';
import { UsersService } from 'src/services/openapi';
import { ContentBox } from 'src/components';
import {
  PublicStatusAction,
  PublicStatusContext,
} from 'src/features/videos/PublicStatusAction';
import RatingsFilter from 'src/features/ratings/RatingsFilter';

function VideoRatingsPage() {
  const prov: PaginatedContributorRatingList = {
    count: 0,
    results: [],
  };
  const [ratings, setRatings] = useState(prov);
  const [isLoading, setIsLoading] = useState(true);
  const location = useLocation();
  const history = useHistory();
  const searchParams = new URLSearchParams(location.search);
  const limit = 20;
  const offset = Number(searchParams.get('offset') || 0);
  const videoCount = ratings.count || 0;

  function handleOffsetChange(newOffset: number) {
    searchParams.set('offset', newOffset.toString());
    history.push('/recommendations/?' + searchParams.toString());
  }

  useEffect(() => {
    setIsLoading(true);
    const loadData = async () => {
      const urlParams = new URLSearchParams(location.search);
      const isPublicParam = urlParams.get('isPublic');
      const isPublic = isPublicParam ? isPublicParam === 'true' : undefined;
      const response = await UsersService.usersMeContributorRatingsList(
        limit,
        offset,
        isPublic
      );
      setRatings(response);
      setIsLoading(false);
    };
    loadData();
  }, [offset, location.search]);

  const videos = (ratings.results || []).map(
    (rating: ContributorRating) => rating.video
  );

  const idToRating = Object.fromEntries(
    (ratings.results || []).map((rating) => [rating.video.video_id, rating])
  );
  const getPublicStatus = (videoId: string) => idToRating[videoId];

  const onRatingChange = (newRating: ContributorRating) => {
    setRatings((prevRatings) => {
      const updatedResults = (prevRatings.results || []).map((rating) =>
        rating.video.video_id === newRating.video.video_id ? newRating : rating
      );
      return { ...prevRatings, results: updatedResults };
    });
  };

  return (
    <ContentBox noMinPadding maxWidth="md">
      <Box px={{ xs: 2, sm: 0 }}>
        <RatingsFilter />
      </Box>
      {isLoading ? (
        <CircularProgress />
      ) : (
        <PublicStatusContext.Provider
          value={{
            getContributorRating: getPublicStatus,
            onChange: onRatingChange,
          }}
        >
          <VideoList videos={videos} settings={[PublicStatusAction]} />
        </PublicStatusContext.Provider>
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

export default VideoRatingsPage;
