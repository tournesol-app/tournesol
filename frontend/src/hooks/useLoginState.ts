import { useAppSelector, useAppDispatch } from 'src/app/hooks';
import {
  selectLogin,
  logout as logoutAction,
} from 'src/features/login/loginSlice';
import { LoginState } from 'src/features/login/LoginState.model';
import { isLoggedIn as isStateLoggedIn } from 'src/features/login/loginUtils';

export const useLoginState = () => {
  const loginState: LoginState = useAppSelector(selectLogin);
  const dispatch = useAppDispatch();

  const logout = () => dispatch(logoutAction());
  const isLoggedIn = isStateLoggedIn(loginState);

  return {
    logout,
    loginState,
    isLoggedIn,
  };
};
