export interface WikiLoginState {
  status: 'idle' | 'loading' | 'failed';
  username?: string;
  logged: boolean;
}
