import React, { useState, useEffect, useCallback } from 'react';
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
  RatingsContext,
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

  const handleOffsetChange = (newOffset: number) => {
    searchParams.set('offset', newOffset.toString());
    history.push({ search: searchParams.toString() });
  };

  const loadData = useCallback(async () => {
    setIsLoading(true);
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
  }, [offset, location.search]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const videos = (ratings.results || []).map(
    (rating: ContributorRating) => rating.video
  );

  const idToRating = Object.fromEntries(
    (ratings.results || []).map((rating) => [rating.video.video_id, rating])
  );
  const getRating = (videoId: string) => idToRating[videoId];

  const onRatingChange = (newRating: ContributorRating | undefined) => {
    if (newRating) {
      setRatings((prevRatings) => {
        const updatedResults = (prevRatings.results || []).map((rating) =>
          rating.video.video_id === newRating.video.video_id
            ? newRating
            : rating
        );
        return { ...prevRatings, results: updatedResults };
      });
    } else {
      // All ratings have been changed.
      if (searchParams.get('isPublic')) {
        // A filter had been selected. Let's reset the filter to reload the list.
        searchParams.delete('isPublic');
        history.push({ search: searchParams.toString() });
      } else {
        // No filter is selected. Let's simply refresh the list.
        loadData();
      }
    }
  };

  return (
    <RatingsContext.Provider
      value={{
        getContributorRating: getRating,
        onChange: onRatingChange,
      }}
    >
      <ContentBox noMinPadding maxWidth="md">
        <Box px={{ xs: 2, sm: 0 }}>
          <RatingsFilter />
        </Box>
        {isLoading ? (
          <CircularProgress />
        ) : (
          <VideoList videos={videos} settings={[PublicStatusAction]} />
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
    </RatingsContext.Provider>
  );
}

export default VideoRatingsPage;
