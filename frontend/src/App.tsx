import React from 'react';
import { Switch, Route, Redirect } from 'react-router-dom';

import { useAppSelector } from './app/hooks';
import { isLoggedIn } from 'src/features/login/loginUtils';
import { selectLogin } from 'src/features/login/loginSlice';
import HomePage from './pages/home/Home';
import LoginPage from './pages/login/Login';
import SettingsAccountPage from './pages/settings/account/Account';
import SettingsProfilePage from './pages/settings/profile/Profile';
import SignupPage from './pages/signup/Signup';
import VerifyUser from './pages/signup/VerifyUser';
import ComparisonListPage from './pages/comparisons/ComparisonList';
import DonatePage from './pages/donate/Donate';
import RateLaterPage from './pages/rateLater/RateLater';
import Frame from './features/frame/Frame';
import ComparisonPage from './pages/comparisons/Comparison';
import { PrivateRoute } from './features/login/PrivateRoute';
import VideoCardPage from './pages/videos/VideoCard';
import VideoRecommendationPage from './pages/videos/VideoRecommendation';

function App() {
  const loginState = useAppSelector(selectLogin);

  return (
    <Frame>
      <Switch>
        <Route path="/video/:video_id">
          <VideoCardPage />
        </Route>
        <Route path="/recommendations">
          <VideoRecommendationPage />
        </Route>
        <Route path="/login">
          <LoginPage />
        </Route>
        <Route path="/settings/profile">
          <SettingsProfilePage />
        </Route>
        <Route path="/settings/account">
          <SettingsAccountPage />
        </Route>
        <PrivateRoute path="/comparisons">
          <ComparisonListPage />
        </PrivateRoute>
        <PrivateRoute path="/comparison">
          <ComparisonPage />
        </PrivateRoute>
        <PrivateRoute path="/rate_later">
          <RateLaterPage />
        </PrivateRoute>
        <Route path="/donate">
          <DonatePage />
        </Route>
        <Route path="/signup">
          {isLoggedIn(loginState) ? <Redirect to="/" /> : <SignupPage />}
        </Route>
        <Route path="/verify-user">
          <VerifyUser />
        </Route>
        <Route path="/">
          <HomePage />
        </Route>
      </Switch>
    </Frame>
  );
}

export default App;
