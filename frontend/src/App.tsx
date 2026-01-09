import React, { useState, useEffect } from 'react';
import { Navigate, Route, Routes, useLocation } from 'react-router-dom';
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
import RouteWrapper from './features/login/RouteWrapper';

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

const ManifestoPage = React.lazy(
  () => import('./pages/manifesto/ManifestoPage')
);

const API_URL = import.meta.env.REACT_APP_API_URL;

const initializeOpenAPI = (
  getValidAccessToken: () => Promise<string | null>,
  i18n: i18nInterface
) => {
  OpenAPI.BASE = API_URL ?? '';
  OpenAPI.TOKEN = async () => (await getValidAccessToken()) ?? '';
  OpenAPI.HEADERS = async () => ({
    // Set the current language in API requests to
    // get localized error messages in the response.
    'accept-language': i18n.resolvedLanguage || i18n.language,
  });
};

const ScrollToTop = () => {
  const { pathname } = useLocation();

  useEffect(() => {
    if (!location.hash) {
      scrollToTop();
    }
  }, [pathname]);

  return null;
};

const buildParentRoutePath = (path: string) => {
  return path.endsWith('/') ? `${path}*` : `${path}/*`;
};

function App() {
  const { i18n } = useTranslation();
  const { isLoggedIn, getValidAccessToken } = useLoginState();

  // `useState` is used here to call initializeOpenAPI before first render
  useState(() => initializeOpenAPI(getValidAccessToken, i18n));

  useEffect(() => {
    initializeOpenAPI(getValidAccessToken, i18n);
  }, [getValidAccessToken, i18n]);

  useRefreshSettings();

  return (
    <PollProvider>
      <StatsLazyProvider>
        <ScrollToTop />
        <Frame>
          <Routes>
            <Route
              path="/actions"
              element={
                <RouteWrapper>
                  <ActionsPage />
                </RouteWrapper>
              }
            />
            {/*
              https://tournesol.app/action is the URL mentionned
              in "La Dictature des Algorithmes" (page 318)
            */}
            <Route
              path="/action"
              element={<Navigate to="/actions" replace />}
            />
            <Route
              path="/faq"
              element={
                <RouteWrapper>
                  <FAQ />
                </RouteWrapper>
              }
            />
            <Route
              path="/events"
              element={
                <RouteWrapper>
                  <AllEvents />
                </RouteWrapper>
              }
            />
            <Route
              path="/live"
              element={
                <RouteWrapper>
                  <TournesolLivePage />
                </RouteWrapper>
              }
            />
            <Route
              path="/talks"
              element={
                <RouteWrapper>
                  <TournesolTalksPage />
                </RouteWrapper>
              }
            />
            {/* About routes */}
            <Route
              path="/about/terms-of-service"
              element={
                <RouteWrapper>
                  <TermsOfService />
                </RouteWrapper>
              }
            />
            <Route
              path="/about/privacy_policy"
              element={
                <RouteWrapper>
                  <PrivacyPolicy />
                </RouteWrapper>
              }
            />
            <Route
              path="/about/trusted_domains"
              element={
                <RouteWrapper>
                  <TrustedDomains />
                </RouteWrapper>
              }
            />
            <Route
              path="/about/donate"
              element={
                <RouteWrapper>
                  <DonatePage />
                </RouteWrapper>
              }
            />
            <Route
              path="/about"
              element={
                <RouteWrapper>
                  <About />
                </RouteWrapper>
              }
            />
            <Route
              path="/manifesto"
              element={
                <RouteWrapper>
                  <ManifestoPage />
                </RouteWrapper>
              }
            />
            {/* LEGAGY route used for retro-compatibility */}
            <Route
              path="/video/:video_id"
              element={
                <RouteWrapper>
                  <VideoAnalysisPage />
                </RouteWrapper>
              }
            />
            {/* User Management routes */}
            <Route
              path="/login"
              element={
                <RouteWrapper>
                  <LoginPage />
                </RouteWrapper>
              }
            />
            <Route
              path="/settings/profile"
              element={
                <RouteWrapper auth={true}>
                  <SettingsProfilePage />
                </RouteWrapper>
              }
            />
            <Route
              path="/settings/account"
              element={
                <RouteWrapper auth={true}>
                  <SettingsAccountPage />
                </RouteWrapper>
              }
            />
            <Route
              path="/settings/preferences"
              element={
                <RouteWrapper auth={true}>
                  <SettingsPreferencesPage />
                </RouteWrapper>
              }
            />
            <Route
              path="/vouching"
              element={
                <RouteWrapper auth={true}>
                  <PersonalVouchersPage />
                </RouteWrapper>
              }
            />
            <Route
              path="/signup"
              element={
                <RouteWrapper>
                  {isLoggedIn ? <Navigate to="/" replace /> : <SignupPage />}
                </RouteWrapper>
              }
            />
            <Route
              path="/verify-user"
              element={
                <RouteWrapper>
                  <VerifySignature verify="user" />
                </RouteWrapper>
              }
            />
            <Route
              path="/verify-email"
              element={
                <RouteWrapper>
                  <VerifySignature verify="email" />
                </RouteWrapper>
              }
            />
            <Route
              path="/forgot"
              element={
                <RouteWrapper>
                  {isLoggedIn ? (
                    <Navigate to="/settings/account" replace />
                  ) : (
                    <ForgotPassword />
                  )}
                </RouteWrapper>
              }
            />
            <Route
              path="/reset-password"
              element={
                <RouteWrapper>
                  <ResetPassword />
                </RouteWrapper>
              }
            />
            <Route
              path="/shared-content"
              element={
                <RouteWrapper>
                  <SharedContent />
                </RouteWrapper>
              }
            />
            {/* Polls */}
            {polls.map(({ name, path }) => (
              <Route
                key={name}
                path={buildParentRoutePath(path)}
                element={<PollRoutes pollName={name}></PollRoutes>}
              />
            ))}
          </Routes>
        </Frame>
      </StatsLazyProvider>
    </PollProvider>
  );
}

export default App;
