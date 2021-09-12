import { LoginState } from './LoginState.model';

export const hasValidToken = (login: LoginState) => {
  if (!login.access_token || !login.access_token_expiration_date) {
    return false;
  }
  const now = new Date();
  const exp = new Date(login.access_token_expiration_date);
  if (now.getTime() > exp.getTime()) {
    return false;
  }
  return true;
};

export const isLoggedIn = (login: LoginState) =>
  login.status === 'idle' && hasValidToken(login);
