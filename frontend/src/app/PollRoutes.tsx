import React, { useEffect } from 'react';
import { Switch, useRouteMatch } from 'react-router-dom';
import { Box, CircularProgress } from '@mui/material';
import PublicRoute from 'src/features/login/PublicRoute';
import PrivateRoute from 'src/features/login/PrivateRoute';
import PageNotFound from 'src/pages/404/PageNotFound';
import ComparisonListPage from 'src/pages/comparisons/ComparisonList';
import FeedbackPage from 'src/pages/personal/feedback/FeedbackPage';
import HomePage from 'src/pages/home/Home';
import VideoRecommendationPage from 'src/pages/videos/VideoRecommendation';
import VideoRatingsPage from 'src/pages/videos/VideoRatings';
import ComparisonPage from 'src/pages/comparisons/Comparison';
import RateLaterPage from 'src/pages/rateLater/RateLater';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import { RouteID } from 'src/utils/types';

interface Props {
  pollName: string;
}

const PollRoutes = ({ pollName }: Props) => {
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
      id: RouteID.Home,
      url: '',
      page: HomePage,
      type: PublicRoute,
    },
    {
      id: RouteID.Recommendations,
      url: 'recommendations',
      page: VideoRecommendationPage,
      type: PublicRoute,
    },
    {
      id: RouteID.Comparison,
      url: 'comparison',
      page: ComparisonPage,
      type: PrivateRoute,
    },
    {
      id: RouteID.MyComparisons,
      url: 'comparisons',
      page: ComparisonListPage,
      type: PrivateRoute,
    },
    {
      id: RouteID.MyComparedItems,
      url: 'ratings',
      page: VideoRatingsPage,
      type: PrivateRoute,
    },
    {
      id: RouteID.MyRateLaterList,
      url: 'rate_later',
      page: RateLaterPage,
      type: PrivateRoute,
    },
    {
      id: RouteID.MyFeedback,
      url: 'personal/feedback',
      page: FeedbackPage,
      type: PrivateRoute,
    },
  ];

  return (
    <Switch>
      {routes.map((route) => {
        if (disabledItems.includes(route.id)) {
          return;
        }
        return (
          <route.type key={route.id} path={`${basePath}/${route.url}`} exact>
            <route.page />
          </route.type>
        );
      })}
      <PublicRoute>
        <PageNotFound />
      </PublicRoute>
    </Switch>
  );
};

export default PollRoutes;
