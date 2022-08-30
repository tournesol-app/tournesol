import React, { useState, useEffect } from 'react';
import { Switch, Redirect } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { i18n as i18nInterface } from 'i18next';

import { useLoginState } from './hooks';
import LoginPage from './pages/login/Login';
import SettingsAccountPage from './pages/settings/account/Account';
import SettingsProfilePage from './pages/settings/profile/Profile';
import SignupPage from './pages/signup/Signup';
import VerifySignature from './pages/signup/Verify';
import DonatePage from './pages/about/Donate';
import PersonalVouchersPage from './pages/personal/vouchers/VouchersPage';
import Frame from './features/frame/Frame';

import PublicRoute from './features/login/PublicRoute';
import PrivateRoute from './features/login/PrivateRoute';

import ForgotPassword from './pages/login/ForgotPassword';
import ResetPassword from './pages/login/ResetPassword';
import TrustedDomains from './pages/about/TrustedDomains';
import PrivacyPolicy from './pages/about/PrivacyPolicy';
import About from './pages/about/About';

import { OpenAPI } from 'src/services/openapi';
import { LoginState } from './features/login/LoginState.model';
import { polls } from './utils/constants';
import PollRoutes from './app/PollRoutes';
import { PollProvider } from './hooks/useCurrentPoll';

// The Analysis Page uses recharts which is a rather big library,
// thus we choose to load it lazily.
// See https://reactjs.org/docs/code-splitting.html#route-based-code-splitting
// for more details.
const VideoAnalysisPage = React.lazy(
  () => import('./pages/videos/VideoAnalysisPage')
);

const API_URL = process.env.REACT_APP_API_URL;

const initializeOpenAPI = (loginState: LoginState, i18n: i18nInterface) => {
  OpenAPI.BASE = API_URL ?? '';
  OpenAPI.TOKEN = async () => loginState.access_token ?? '';
  OpenAPI.HEADERS = async () => ({
    // Set the current language in API requests to
    // get localized error messages in the response.
    'accept-language': i18n.resolvedLanguage,
  });
};

function App() {
  const { i18n } = useTranslation();
  const { isLoggedIn, loginState } = useLoginState();

  // `useState` is used here to call initializeOpenAPI before first render
  useState(() => initializeOpenAPI(loginState, i18n));
  useEffect(() => {
    initializeOpenAPI(loginState, i18n);
  }, [loginState, i18n]);

  return (
    <PollProvider>
      <Frame>
        <Switch>
          {/* About routes */}
          <PublicRoute path="/about/privacy_policy">
            <PrivacyPolicy />
          </PublicRoute>
          <PublicRoute path="/about/trusted_domains">
            <TrustedDomains />
          </PublicRoute>
          <PublicRoute path="/about/donate">
            <DonatePage />
          </PublicRoute>
          <PublicRoute path="/about">
            <About />
          </PublicRoute>
          {/* LEGAGY route used for retro-compatibility */}
          <PublicRoute path="/video/:video_id">
            <VideoAnalysisPage />
          </PublicRoute>
          {/* User Management routes */}
          <PublicRoute path="/login">
            <LoginPage />
          </PublicRoute>
          <PrivateRoute path="/settings/profile">
            <SettingsProfilePage />
          </PrivateRoute>
          <PrivateRoute path="/settings/account">
            <SettingsAccountPage />
          </PrivateRoute>
          <PrivateRoute path="/personal-vouchers">
            <PersonalVouchersPage />
          </PrivateRoute>
          <PublicRoute path="/signup">
            {isLoggedIn ? <Redirect to="/" /> : <SignupPage />}
          </PublicRoute>
          <PublicRoute path="/verify-user">
            <VerifySignature verify="user" />
          </PublicRoute>
          <PublicRoute path="/verify-email">
            <VerifySignature verify="email" />
          </PublicRoute>
          <PublicRoute path="/forgot">
            {isLoggedIn ? (
              <Redirect to="/settings/account" />
            ) : (
              <ForgotPassword />
            )}
          </PublicRoute>
          <PublicRoute path="/reset-password">
            <ResetPassword />
          </PublicRoute>
          {/* Polls */}
          {polls.map(({ name, path }) => (
            <PublicRoute key={name} path={path}>
              <PollRoutes pollName={name}></PollRoutes>
            </PublicRoute>
          ))}
        </Switch>
      </Frame>
    </PollProvider>
  );
}

export default App;
