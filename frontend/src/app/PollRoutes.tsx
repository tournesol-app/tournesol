import React, { useEffect, useContext, useState } from 'react';
import { Switch, useRouteMatch } from 'react-router-dom';
import PublicRoute from 'src/features/login/PublicRoute';
import PrivateRoute from 'src/features/login/PrivateRoute';
import ComparisonListPage from 'src/pages/comparisons/ComparisonList';
import VideoRecommendationPage from 'src/pages/videos/VideoRecommendation';
import VideoRatingsPage from 'src/pages/videos/VideoRatings';
import ComparisonPage from 'src/pages/comparisons/Comparison';
import RateLaterPage from 'src/pages/rateLater/RateLater';
import { PollContext } from 'src/app/poll';

interface Props {
  pollName: string;
  disableRecommendations?: boolean;
}

const PollRoutes = ({ pollName, disableRecommendations = false }: Props) => {
  const { path } = useRouteMatch();
  const basePath = path.replace(/\/+$/g, '');

  const { setPollName } = useContext(PollContext);

  useEffect(() => {
    setPollName(() => pollName);
  });

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
      <PublicRoute>404</PublicRoute>
    </Switch>
  );
};

export default PollRoutes;
