import React, { useEffect } from 'react';
import { Navigate, useLocation } from 'react-router-dom';

import { useAppSelector, useAppDispatch } from 'src/app/hooks';
import {
  getTokenFromRefreshAsync,
  selectLogin,
} from 'src/features/login/loginSlice';
import { isLoggedIn } from 'src/features/login/loginUtils';

// The token should be refreshed if it expires in less than 10 minutes.
const TOKEN_MIN_VALIDITY_MS = 600000;

/**
 * A wrapper around the element rendered by the React Router <Route> component.
 *
 * Should be used to trigger code when the route changes.
 */
const RouteWrapper = ({
  children,
  auth = false,
}: {
  children: React.ReactNode;
  auth?: boolean;
}) => {
  const dispatch = useAppDispatch();
  const login = useAppSelector(selectLogin);
  const location = useLocation();

  useEffect(() => {
    const should_refresh =
      !isLoggedIn(login) ||
      !login.access_token_expiration_date ||
      new Date(login.access_token_expiration_date) <
        new Date(new Date().getTime() + TOKEN_MIN_VALIDITY_MS);

    if (login.status !== 'loading' && login.refresh_token && should_refresh) {
      console.log(
        'Access token invalid but refresh token present, trying to refresh.'
      );
      dispatch(getTokenFromRefreshAsync(login.refresh_token));
    }
  }, [login, dispatch]);

  if (auth && !isLoggedIn(login)) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <>{children}</>;
};

export default RouteWrapper;
