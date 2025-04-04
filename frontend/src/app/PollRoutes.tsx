import React, { useEffect } from 'react';
import { Switch, useRouteMatch } from 'react-router-dom';

import { Box, CircularProgress } from '@mui/material';

import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import PublicRoute from 'src/features/login/PublicRoute';
import PrivateRoute from 'src/features/login/PrivateRoute';
import PwaEntryPoint from 'src/features/pwa/PwaEntryPoint';
import PageNotFound from 'src/pages/404/PageNotFound';
import ComparisonListPage from 'src/pages/comparisons/ComparisonList';
import CriteriaPage from 'src/pages/criteria/CriteriaPage';
import FeedbackPage from 'src/pages/personal/feedback/FeedbackPage';
import EntityAnalysisPage from 'src/pages/entities/EntityAnalysisPage';
import HomePage from 'src/pages/home/Home';
import PersonalStatsPage from 'src/pages/me/stats/PersonalStatsPage';
import ProofByKeywordPage from 'src/pages/me/proof/ProofByKeywordPage';
import RecommendationPage from 'src/pages/recommendations/RecommendationPage';
import VideoRatingsPage from 'src/pages/videos/VideoRatings';
import ComparisonPage from 'src/pages/comparisons/Comparison';
import FeedForYou from 'src/pages/feed/FeedForYou';
import FeedTopItems from 'src/pages/feed/FeedTopItems';
import RateLaterPage from 'src/pages/rateLater/RateLater';
import SearchPage from 'src/pages/search/SearchPage';
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
      id: RouteID.PwaEntryPoint,
      url: 'pwa/start',
      page: PwaEntryPoint,
      type: PublicRoute,
    },
    // deprecated, kept for backward compatibility, should be deleted later
    // in 2025
    {
      id: RouteID.FeedCollectiveRecommendations,
      url: 'feed/recommendations',
      page: PwaEntryPoint,
      type: PublicRoute,
    },
    {
      id: RouteID.FeedTopItems,
      url: 'feed/top',
      page: FeedTopItems,
      type: PublicRoute,
    },
    {
      id: RouteID.FeedForYou,
      url: 'feed/foryou',
      page: FeedForYou,
      type: PrivateRoute,
    },
    {
      id: RouteID.Search,
      url: 'search',
      page: SearchPage,
      type: PublicRoute,
    },
    // deprecated, kept for backward compatibility, should be deleted later
    // in 2025
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
    {
      id: RouteID.MyProofByKeyword,
      url: 'me/proof/:keyword',
      page: ProofByKeywordPage,
      type: PrivateRoute,
    },
    {
      id: RouteID.MyStats,
      url: 'me/stats',
      page: PersonalStatsPage,
      type: PrivateRoute,
    },
    {
      id: RouteID.Criteria,
      url: 'criteria',
      page: CriteriaPage,
      type: PublicRoute,
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
