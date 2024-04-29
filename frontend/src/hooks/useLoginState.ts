import { useCallback } from 'react';
import { useAppSelector, useAppDispatch } from 'src/app/hooks';
import {
  selectLogin,
  logout as logoutAction,
  updateUsername as updateUsernameAction,
} from 'src/features/login/loginSlice';
import { clearSettings } from 'src/features/settings/userSettingsSlice';
import { LoginState } from 'src/features/login/LoginState.model';
import { isLoggedIn as isStateLoggedIn } from 'src/features/login/loginUtils';
import { autoSuggestionPool } from 'src/features/suggestions/suggestionPool';

export const useLoginState = () => {
  const loginState: LoginState = useAppSelector(selectLogin);
  const dispatch = useAppDispatch();

  const logout = useCallback(() => {
    dispatch(logoutAction());
    /**
     * Ensure that the user's settings retrieved after the login are cleared
     * after a logout, to not leave trace of the user's preferences in the
     * browser.
     */
    dispatch(clearSettings());
    autoSuggestionPool.clear();
  }, [dispatch]);

  const updateUsername = useCallback(
    (username: string) => {
      dispatch(updateUsernameAction({ username: username }));
    },
    [dispatch]
  );
  const isLoggedIn = isStateLoggedIn(loginState);

  return {
    logout,
    updateUsername,
    loginState,
    isLoggedIn,
  };
};
