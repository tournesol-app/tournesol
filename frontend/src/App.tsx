import React, { useState, useEffect } from 'react';
import { Switch, Route, Redirect } from 'react-router-dom';

import { useLoginState } from './hooks';
import HomePage from './pages/home/Home';
import LoginPage from './pages/login/Login';
import SettingsAccountPage from './pages/settings/account/Account';
import SettingsProfilePage from './pages/settings/profile/Profile';
import SignupPage from './pages/signup/Signup';
import VerifySignature from './pages/signup/Verify';
import ComparisonListPage from './pages/comparisons/ComparisonList';
import DonatePage from './pages/about/Donate';
import RateLaterPage from './pages/rateLater/RateLater';
import Frame from './features/frame/Frame';
import ComparisonPage from './pages/comparisons/Comparison';
import { PrivateRoute } from './features/login/PrivateRoute';
import VideoCardPage from './pages/videos/VideoCard';
import VideoRecommendationPage from './pages/videos/VideoRecommendation';
import VideoRatingsPage from './pages/videos/VideoRatings';
import ForgotPassword from './pages/login/ForgotPassword';
import ResetPassword from './pages/login/ResetPassword';
import TrustedDomains from './pages/about/TrustedDomains';
import PrivacyPolicy from './pages/about/PrivacyPolicy';
import About from './pages/about/About';

import { OpenAPI } from 'src/services/openapi';
import { LoginState } from './features/login/LoginState.model';

const API_URL = process.env.REACT_APP_API_URL;

const initializeOpenAPI = (loginState: LoginState) => {
  OpenAPI.BASE = API_URL ?? '';
  OpenAPI.TOKEN = async () => loginState.access_token ?? '';
};

function App() {
  const { isLoggedIn, loginState } = useLoginState();
  // `useState` is used here to call initializeOpenAPI before first render
  useState(() => initializeOpenAPI(loginState));

  useEffect(() => {
    initializeOpenAPI(loginState);
  }, [loginState]);

  return (
    <Frame>
      <Switch>
        {/* About routes */}
        <Route path="/about/privacy_policy">
          <PrivacyPolicy />
        </Route>
        <Route path="/about/trusted_domains">
          <TrustedDomains />
        </Route>
        <Route path="/about/donate">
          <DonatePage />
        </Route>
        <Route path="/about">
          <About />
        </Route>
        {/* Videos and Comparisons routes */}
        <Route path="/video/:video_id">
          <VideoCardPage />
        </Route>
        <Route path="/recommendations">
          <VideoRecommendationPage />
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
        <PrivateRoute path="/ratings">
          <VideoRatingsPage />
        </PrivateRoute>
        {/* User Management routes */}
        <Route path="/login">
          <LoginPage />
        </Route>
        <PrivateRoute path="/settings/profile">
          <SettingsProfilePage />
        </PrivateRoute>
        <PrivateRoute path="/settings/account">
          <SettingsAccountPage />
        </PrivateRoute>
        <Route path="/signup">
          {isLoggedIn ? <Redirect to="/" /> : <SignupPage />}
        </Route>
        <Route path="/verify-user">
          <VerifySignature verify="user" />
        </Route>
        <Route path="/verify-email">
          <VerifySignature verify="email" />
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
        {/* Home page */}
        <Route path="/">
          <HomePage />
        </Route>
      </Switch>
    </Frame>
  );
}

export default App;
