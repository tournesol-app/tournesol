import { useCallback } from 'react';
import { useAppSelector, useAppDispatch } from 'src/app/hooks';
import {
  selectLogin,
  logout as logoutAction,
  updateUsername as updateUsernameAction,
} from 'src/features/login/loginSlice';
import { LoginState } from 'src/features/login/LoginState.model';
import { isLoggedIn as isStateLoggedIn } from 'src/features/login/loginUtils';

export const useLoginState = () => {
  const loginState: LoginState = useAppSelector(selectLogin);
  const dispatch = useAppDispatch();

  const logout = useCallback(() => {
    dispatch(logoutAction());
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
