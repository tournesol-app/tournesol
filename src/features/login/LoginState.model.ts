import { UserInfo } from './UserInfo.model';

export interface LoginState {
  logged: boolean;
  access_token: string;
  access_token_expiration_date: string;
  refresh_token: string;
  id_token: string;
  user_info?: UserInfo;
  status: 'idle' | 'loading' | 'failed';
}
