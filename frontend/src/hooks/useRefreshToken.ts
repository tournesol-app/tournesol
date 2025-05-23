import { useEffect } from 'react';

import { useAppSelector, useAppDispatch } from 'src/app/hooks';
import {
  getTokenFromRefreshAsync,
  selectLogin,
} from 'src/features/login/loginSlice';
import { isLoggedIn } from 'src/features/login/loginUtils';

// The token should be refreshed if it expires in less than 10 minutes.
const TOKEN_MIN_VALIDITY_MS = 600000;

/**
 * Refresh the user access token if needed.
 */
export const useRefreshToken = () => {
  const dispatch = useAppDispatch();
  const login = useAppSelector(selectLogin);

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
};
