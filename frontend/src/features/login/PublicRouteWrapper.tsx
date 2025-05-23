import React, { useEffect } from 'react';

import { useAppSelector, useAppDispatch } from 'src/app/hooks';
import { selectLogin, getTokenFromRefreshAsync } from './loginSlice';
import { isLoggedIn } from './loginUtils';
import { LoginState } from './LoginState.model';

const PublicRouteWrapper = ({ children }: { children: React.ReactNode }) => {
  const login: LoginState = useAppSelector(selectLogin);
  const dispatch = useAppDispatch();

  useEffect(() => {
    const should_refresh =
      !isLoggedIn(login) ||
      !login.access_token_expiration_date ||
      // the token should be refreshed if it expires in less than 10 minutes
      new Date(login.access_token_expiration_date) <
        new Date(new Date().getTime() + 600000);

    if (login.status !== 'loading' && login.refresh_token && should_refresh) {
      console.log('token invalid but refresh token present, trying to refresh');
      dispatch(getTokenFromRefreshAsync(login.refresh_token));
    }
  }, [login, dispatch]);

  return <>{children}</>;
};

export default PublicRouteWrapper;
