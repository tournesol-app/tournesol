import React, { useState, useEffect } from 'react';
import { Route } from 'react-router-dom';

import { useAppSelector, useAppDispatch } from 'src/app/hooks';
import { selectLogin, getTokenFromRefreshAsync } from './loginSlice';
import { LoginState } from './LoginState.model';
import { isLoggedIn } from './loginUtils';

interface Props {
  [propName: string]: unknown;
}

const PublicRoute = (props: Props) => {
  const login: LoginState = useAppSelector(selectLogin);
  const dispatch = useAppDispatch();
  const [shouldTryRefresh, setShouldTryRefresh] = useState(true);

  useEffect(() => {
    if (shouldTryRefresh && login.refresh_token && !isLoggedIn(login)) {
      console.log('token invalid but refresh token present, trying to refresh');
      setShouldTryRefresh(false);
      dispatch(getTokenFromRefreshAsync(login.refresh_token));
    }
  }, [shouldTryRefresh, login, dispatch]);

  return <Route {...props} />;
};

export default PublicRoute;
