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

  const {
    setPollName,
    name: currentPollName,
    options,
    isReady,
  } = useCurrentPoll();
  const disabledItems = options?.disabledRouteIds ?? [];

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

  const routes = [
    {
      id: 'myComparisons',
      url: 'comparisons',
      page: ComparisonListPage,
    },
    {
      id: 'comparison',
      url: 'comparison',
      page: ComparisonPage,
    },
    {
      id: 'myRateLaterList',
      url: 'rate_later',
      page: RateLaterPage,
    },
    {
      id: 'myRatedVideos',
      url: 'ratings',
      page: VideoRatingsPage,
    },
  ] as const;

  return (
    <Switch>
      {!disableRecommendations && (
        <PublicRoute path={`${basePath}/recommendations`}>
          <VideoRecommendationPage />
        </PublicRoute>
      )}
      {routes.map((route) => {
        if (disabledItems.includes(route.id)) {
          return;
        }
        return (
          <PrivateRoute key={route.id} path={`${basePath}/${route.url}`}>
            <route.page />
          </PrivateRoute>
        );
      })}
      <PublicRoute>Page not found</PublicRoute>
    </Switch>
  );
};

export default PollRoutes;
