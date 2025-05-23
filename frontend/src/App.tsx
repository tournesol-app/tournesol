import React, { useState, useEffect } from 'react';
import { Switch, Redirect, useLocation, Route } from 'react-router-dom';
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
            <Route
              path="/actions"
              render={() => (
                <RouteWrapper>
                  <ActionsPage />
                </RouteWrapper>
              )}
            />
            <Route path="/action" render={() => <Redirect to="/actions" />} />
            <Route
              path="/faq"
              render={() => (
                <RouteWrapper>
                  <FAQ />
                </RouteWrapper>
              )}
            />
            <Route
              path="/events"
              render={() => (
                <RouteWrapper>
                  <AllEvents />
                </RouteWrapper>
              )}
            />
            <Route
              path="/live"
              render={() => (
                <RouteWrapper>
                  <TournesolLivePage />
                </RouteWrapper>
              )}
            />
            <Route
              path="/talks"
              render={() => (
                <RouteWrapper>
                  <TournesolTalksPage />
                </RouteWrapper>
              )}
            />
            {/* About routes */}
            <Route
              path="/about/terms-of-service"
              render={() => (
                <RouteWrapper>
                  <TermsOfService />
                </RouteWrapper>
              )}
            />
            <Route
              path="/about/privacy_policy"
              render={() => (
                <RouteWrapper>
                  <PrivacyPolicy />
                </RouteWrapper>
              )}
            />
            <Route
              path="/about/trusted_domains"
              render={() => (
                <RouteWrapper>
                  <TrustedDomains />
                </RouteWrapper>
              )}
            />
            <Route
              path="/about/donate"
              render={() => (
                <RouteWrapper>
                  <DonatePage />
                </RouteWrapper>
              )}
            />
            <Route
              path="/about"
              render={() => (
                <RouteWrapper>
                  <About />
                </RouteWrapper>
              )}
            />
            {/* LEGAGY route used for retro-compatibility */}
            <Route
              path="/video/:video_id"
              render={() => (
                <RouteWrapper>
                  <VideoAnalysisPage />
                </RouteWrapper>
              )}
            />
            {/* User Management routes */}
            <Route
              path="/login"
              render={() => (
                <RouteWrapper>
                  <LoginPage />
                </RouteWrapper>
              )}
            />
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
            <Route
              path="/signup"
              render={() => (
                <RouteWrapper>
                  {isLoggedIn ? <Redirect to="/" /> : <SignupPage />}
                </RouteWrapper>
              )}
            />
            <Route
              path="/verify-user"
              render={() => (
                <RouteWrapper>
                  <VerifySignature verify="user" />
                </RouteWrapper>
              )}
            />
            <Route
              path="/verify-email"
              render={() => (
                <RouteWrapper>
                  <VerifySignature verify="email" />
                </RouteWrapper>
              )}
            />
            <Route
              path="/forgot"
              render={() => (
                <RouteWrapper>
                  {isLoggedIn ? (
                    <Redirect to="/settings/account" />
                  ) : (
                    <ForgotPassword />
                  )}
                </RouteWrapper>
              )}
            />
            <Route
              path="/reset-password"
              render={() => (
                <RouteWrapper>
                  <ResetPassword />
                </RouteWrapper>
              )}
            />
            <Route
              path="/shared-content"
              render={() => (
                <RouteWrapper>
                  <SharedContent />
                </RouteWrapper>
              )}
            />
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
