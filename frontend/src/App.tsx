import React, { useState, useEffect } from 'react';
import { Switch, Redirect, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { i18n as i18nInterface } from 'i18next';

import { useLoginState, useRefreshSettings } from './hooks';
import LoginPage from './pages/login/Login';
import SettingsAccountPage from './pages/settings/account/Account';
import SettingsProfilePage from './pages/settings/profile/Profile';
import SettingsPreferencesPage from './pages/settings/preferences/Preferences';
import SignupPage from './pages/signup/Signup';
import VerifySignature from './pages/signup/Verify';
import DonatePage from './pages/about/Donate';
import PersonalVouchersPage from './pages/personal/vouchers/VouchersPage';
import Frame from './features/frame/Frame';

import { StatsLazyProvider } from './features/statistics/StatsContext';
import PublicRoute from './features/login/PublicRoute';
import PrivateRoute from './features/login/PrivateRoute';

import ActionsPage from './pages/actions/ActionsPage';
import ForgotPassword from './pages/login/ForgotPassword';
import ResetPassword from './pages/login/ResetPassword';
import TrustedDomains from './pages/about/TrustedDomains';
import PrivacyPolicy from './pages/about/PrivacyPolicy';
import TermsOfService from './pages/about/TermsOfService/TermsOfService';
import About from './pages/about/About';
import AllEvents from './pages/events/AllEventsPage';
import TournesolLivePage from './pages/events/TournesolLivePage';
import TournesolTalksPage from './pages/events/TournesolTalksPage';
import FAQ from './pages/faq/FAQ';

import { OpenAPI } from 'src/services/openapi';
import { LoginState } from './features/login/LoginState.model';
import { polls } from './utils/constants';
import SharedContent from './app/SharedContent';
import PollRoutes from './app/PollRoutes';
import { PollProvider } from './hooks/useCurrentPoll';
import { scrollToTop } from './utils/ui';

// The Analysis Page uses recharts which is a rather big library,
// thus we choose to load it lazily.
// See https://reactjs.org/docs/code-splitting.html#route-based-code-splitting
// for more details.
const VideoAnalysisPage = React.lazy(
  () => import('./pages/videos/VideoAnalysisPage')
);

const API_URL = import.meta.env.REACT_APP_API_URL;

const initializeOpenAPI = (loginState: LoginState, i18n: i18nInterface) => {
  OpenAPI.BASE = API_URL ?? '';
  OpenAPI.TOKEN = async () => loginState.access_token ?? '';
  OpenAPI.HEADERS = async () => ({
    // Set the current language in API requests to
    // get localized error messages in the response.
    'accept-language': i18n.resolvedLanguage || i18n.language,
  });
};

const ScrollToTop = () => {
  const { pathname } = useLocation();

  useEffect(() => {
    scrollToTop();
  }, [pathname]);

  return null;
};

function App() {
  const { i18n } = useTranslation();
  const { isLoggedIn, loginState } = useLoginState();

  // `useState` is used here to call initializeOpenAPI before first render
  useState(() => initializeOpenAPI(loginState, i18n));

  useEffect(() => {
    initializeOpenAPI(loginState, i18n);
  }, [loginState, i18n]);

  useRefreshSettings();

  return (
    <PollProvider>
      <StatsLazyProvider>
        <ScrollToTop />
        <Frame>
          <Switch>
            <PublicRoute path="/actions">
              <ActionsPage />
            </PublicRoute>
            <PublicRoute path="/action">
              {/*
                https://tournesol.app/action is the URL mentionned
                in "La Dictature des Algorithmes" (page 318)
              */}
              <Redirect to="/actions" />
            </PublicRoute>
            <PublicRoute path="/faq">
              <FAQ />
            </PublicRoute>
            <PublicRoute path="/events">
              <AllEvents />
            </PublicRoute>
            <PublicRoute path="/live">
              <TournesolLivePage />
            </PublicRoute>
            <PublicRoute path="/talks">
              <TournesolTalksPage />
            </PublicRoute>
            {/* About routes */}
            <PublicRoute path="/about/terms-of-service">
              <TermsOfService />
            </PublicRoute>
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
            <PrivateRoute path="/settings/preferences">
              <SettingsPreferencesPage />
            </PrivateRoute>
            <PrivateRoute path="/vouching">
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
            <PublicRoute path="/shared-content">
              <SharedContent />
            </PublicRoute>
            {/* Polls */}
            {polls.map(({ name, path }) => (
              <PublicRoute key={name} path={path}>
                <PollRoutes pollName={name}></PollRoutes>
              </PublicRoute>
            ))}
          </Switch>
        </Frame>
      </StatsLazyProvider>
    </PollProvider>
  );
}

export default App;
