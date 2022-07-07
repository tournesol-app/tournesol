import React, { useEffect } from 'react';
import { Switch, useRouteMatch } from 'react-router-dom';
import { Box, CircularProgress } from '@mui/material';
import PublicRoute from 'src/features/login/PublicRoute';
import PrivateRoute from 'src/features/login/PrivateRoute';
import PageNotFound from 'src/pages/404/PageNotFound';
import ComparisonListPage from 'src/pages/comparisons/ComparisonList';
import FeedbackPage from 'src/pages/personal/feedback/FeedbackPage';
import EntityAnalysisPage from 'src/pages/entities/EntityAnalysisPage';
import HomePage from 'src/pages/home/Home';
import RecommendationPage from 'src/pages/recommendations/RecommendationPage';
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
  const allowPublicPersonalRecommendations =
    options?.allowPublicPersonalRecommendations ?? false;

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
      id: RouteID.CollectiveRecommendations,
      url: 'recommendations',
      page: RecommendationPage,
      type: PublicRoute,
    },
    {
      id: RouteID.EntityAnalysis,
      url: 'entities/:uid',
      page: EntityAnalysisPage,
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

  if (allowPublicPersonalRecommendations) {
    routes.push({
      id: RouteID.PublicPersonalRecommendationsPage,
      url: 'users/:username/recommendations',
      page: RecommendationPage,
      type: PublicRoute,
    });
  }

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
