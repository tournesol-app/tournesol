export interface LoginState {
  access_token?: string;
  access_token_expiration_date?: string;
  refresh_token?: string;
  status: 'idle' | 'loading' | 'failed';
  username?: string;
}
