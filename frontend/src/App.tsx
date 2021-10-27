import React from 'react';
import { Switch, Route, Redirect } from 'react-router-dom';

import { useLoginState } from './hooks';
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
import ForgotPassword from './pages/login/ForgotPassword';
import ResetPassword from './pages/login/ResetPassword';

function App() {
  const { isLoggedIn } = useLoginState();

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
        <PrivateRoute path="/settings/profile">
          <SettingsProfilePage />
        </PrivateRoute>
        <PrivateRoute path="/settings/account">
          <SettingsAccountPage />
        </PrivateRoute>
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
          {isLoggedIn ? <Redirect to="/" /> : <SignupPage />}
        </Route>
        <Route path="/verify-user">
          <VerifyUser />
        </Route>
        <Route path="/forgot">
          {isLoggedIn ? (
            <Redirect to="/settings/account" />
          ) : (
            <ForgotPassword />
          )}
        </Route>
        <Route path="/reset-password">
          <ResetPassword />
        </Route>
        <Route path="/">
          <HomePage />
        </Route>
      </Switch>
    </Frame>
  );
}

export default App;
