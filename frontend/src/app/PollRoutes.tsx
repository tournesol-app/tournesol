import React, { useEffect } from 'react';
import { Route, Routes } from 'react-router-dom';

import { Box, CircularProgress } from '@mui/material';

import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import RouteWrapper from 'src/features/login/RouteWrapper';
import PwaEntryPoint from 'src/features/pwa/PwaEntryPoint';
import PageNotFound from 'src/pages/404/PageNotFound';
import ComparisonListPage from 'src/pages/comparisons/ComparisonList';
import CriteriaPage from 'src/pages/criteria/CriteriaPage';
import FeedbackPage from 'src/pages/personal/feedback/FeedbackPage';
import EntityAnalysisPage from 'src/pages/entities/EntityAnalysisPage';
import HomePage from 'src/pages/home/Home';
import ProofByKeywordPage from 'src/pages/me/proof/ProofByKeywordPage';
import UserActivityStatsPage from 'src/pages/me/stats/UserActivityStatsPage';
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
      <Box
        sx={{
          m: 4,
          textAlign: 'center',
        }}
      >
        <CircularProgress color="secondary" size={50} />
      </Box>
    );
  }

  const routes = [
    {
      id: RouteID.Home,
      url: '',
      page: HomePage,
      auth: false,
    },
    {
      id: RouteID.PwaEntryPoint,
      url: 'pwa/start',
      page: PwaEntryPoint,
      auth: false,
    },
    // deprecated, kept for backward compatibility, should be deleted later
    // in 2025
    {
      id: RouteID.FeedCollectiveRecommendations,
      url: 'feed/recommendations',
      page: PwaEntryPoint,
      auth: false,
    },
    {
      id: RouteID.FeedTopItems,
      url: 'feed/top',
      page: FeedTopItems,
      auth: false,
    },
    {
      id: RouteID.FeedForYou,
      url: 'feed/foryou',
      page: FeedForYou,
      auth: true,
    },
    {
      id: RouteID.Search,
      url: 'search',
      page: SearchPage,
      auth: false,
    },
    // deprecated, kept for backward compatibility, should be deleted later
    // in 2025
    {
      id: RouteID.CollectiveRecommendations,
      url: 'recommendations',
      page: RecommendationPage,
      auth: false,
    },
    {
      id: RouteID.EntityAnalysis,
      url: 'entities/:uid',
      page: EntityAnalysisPage,
      auth: false,
    },
    {
      id: RouteID.Comparison,
      url: 'comparison',
      page: ComparisonPage,
      auth: true,
    },
    {
      id: RouteID.MyComparisons,
      url: 'comparisons',
      page: ComparisonListPage,
      auth: true,
    },
    {
      id: RouteID.MyComparedItems,
      url: 'ratings',
      page: VideoRatingsPage,
      auth: true,
    },
    {
      id: RouteID.MyRateLaterList,
      url: 'rate_later',
      page: RateLaterPage,
      auth: true,
    },
    {
      id: RouteID.MyFeedback,
      url: 'personal/feedback',
      page: FeedbackPage,
      auth: true,
    },
    {
      id: RouteID.MyProofByKeyword,
      url: 'me/proof/:keyword',
      page: ProofByKeywordPage,
      auth: true,
    },
    {
      id: RouteID.MyStats,
      url: 'me/stats',
      page: UserActivityStatsPage,
      type: PrivateRoute,
    },
    {
      id: RouteID.Criteria,
      url: 'criteria',
      page: CriteriaPage,
      auth: false,
    },
  ];

  if (allowPublicPersonalRecommendations) {
    routes.push({
      id: RouteID.PublicPersonalRecommendationsPage,
      url: 'users/:username/recommendations',
      page: RecommendationPage,
      auth: false,
    });
  }

  return (
    <Routes>
      {routes.map((route) => {
        if (disabledItems.includes(route.id)) {
          return;
        }
        return (
          <Route
            key={route.id}
            path={route.url}
            element={
              <RouteWrapper auth={route.auth}>
                <route.page />
              </RouteWrapper>
            }
          />
        );
      })}
      <Route
        path="*"
        element={
          <RouteWrapper>
            <PageNotFound />
          </RouteWrapper>
        }
      ></Route>
    </Routes>
  );
};

export default PollRoutes;
