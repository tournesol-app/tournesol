import React, { useEffect } from 'react';
import { Switch, useRouteMatch } from 'react-router-dom';
import { CircularProgress, Box } from '@mui/material';
import PublicRoute from 'src/features/login/PublicRoute';
import PrivateRoute from 'src/features/login/PrivateRoute';
import ComparisonListPage from 'src/pages/comparisons/ComparisonList';
import VideoRecommendationPage from 'src/pages/videos/VideoRecommendation';
import VideoRatingsPage from 'src/pages/videos/VideoRatings';
import ComparisonPage from 'src/pages/comparisons/Comparison';
import RateLaterPage from 'src/pages/rateLater/RateLater';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';

interface Props {
  pollName: string;
  disableRecommendations?: boolean;
}

const PollRoutes = ({ pollName, disableRecommendations = false }: Props) => {
  const { path } = useRouteMatch();
  const basePath = path.replace(/\/+$/g, '');

  const { setPollName, name: currentPollName, isReady } = useCurrentPoll();

  useEffect(() => {
    if (currentPollName !== pollName || !isReady) {
      setPollName(pollName);
    }
  }, [setPollName, pollName, currentPollName, isReady]);

  if (pollName !== currentPollName || !isReady) {
    return (
      <Box m={4} textAlign="center">
        <CircularProgress color="secondary" size={50} />
      </Box>
    );
  }

  return (
    <Switch>
      {!disableRecommendations && (
        <PublicRoute path={`${basePath}/recommendations`}>
          <VideoRecommendationPage />
        </PublicRoute>
      )}
      <PrivateRoute path={`${basePath}/comparisons`}>
        <ComparisonListPage />
      </PrivateRoute>
      <PrivateRoute path={`${basePath}/comparison`}>
        <ComparisonPage />
      </PrivateRoute>
      <PrivateRoute path={`${basePath}/rate_later`}>
        <RateLaterPage />
      </PrivateRoute>
      <PrivateRoute path={`${basePath}/ratings`}>
        <VideoRatingsPage />
      </PrivateRoute>
      <PublicRoute>Page not found</PublicRoute>
    </Switch>
  );
};

export default PollRoutes;
