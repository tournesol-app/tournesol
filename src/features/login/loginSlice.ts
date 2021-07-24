import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import { RootState } from '../../app/store';
import { fetchAuthorization, fetchLogin, fetchToken, fetchTokenFromRefresh, fetchUserInfo } from './loginAPI';

export interface LoginState {
  logged: boolean;
  code: string;
  access_token: string;
  access_token_expiration_date: string;
  refresh_token: string;
  id_token: string;
  user_info: string;
  status: 'idle' | 'loading' | 'failed';
}

const initialState: LoginState = {
  logged: false,
  code: '',
  access_token: '',
  access_token_expiration_date: '',
  refresh_token: '',
  id_token: '',
  user_info: '',
  status: 'idle',
};

export const getLoginAsync = createAsyncThunk(
  'login/fetchLogin',
  async ({ username, password }: { username: string, password: string }) => {
    await fetchLogin(username, password);
  }
);

export const getAuthorizationAsync = createAsyncThunk(
  'login/fetchAuthorization',
  async () => {
    const response = await fetchAuthorization();
    return response.data;
  }
);

export const getTokenAsync = createAsyncThunk(
  'login/fetchToken',
  async (code: string) => {
    const response = await fetchToken(code);
    return response.data;
  }
);

export const getTokenFromRefreshAsync = createAsyncThunk(
  'login/fetchTokenFromRefresh',
  async (refresh_token: string) => {
    const response = await fetchTokenFromRefresh(refresh_token);
    return response.data;
  }
);

export const getUserInfoAsync = createAsyncThunk(
  'login/fetchUserInfo',
  async (access_token: string) => {
    const response = await fetchUserInfo(access_token);
    return response.data;
  }
);

export const loginSlice = createSlice({
  name: 'login',
  initialState,
  reducers: {
  },
  extraReducers: (builder) => {
    builder
      .addCase(getLoginAsync.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(getLoginAsync.fulfilled, (state, action) => {
        state.status = 'idle';
        state.logged = true;
      })
      .addCase(getLoginAsync.rejected, (state, action) => {
        state.status = 'idle';
      })
      .addCase(getAuthorizationAsync.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(getAuthorizationAsync.fulfilled, (state, action) => {
        state.status = 'idle';
        state.code = action.payload;
      })
      .addCase(getAuthorizationAsync.rejected, (state, action) => {
        state.status = 'idle';
      })
      .addCase(getTokenAsync.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(getTokenAsync.fulfilled, (state, action) => {
        state.status = 'idle';
        state.access_token = action.payload.access_token;
        let exp = new Date()
        exp.setTime(new Date().getTime() + 1000 * action.payload.expires_in);
        state.access_token_expiration_date = exp.toString();
        state.refresh_token = action.payload.refresh_token;
        state.id_token = action.payload.id_token;
      })
      .addCase(getTokenAsync.rejected, (state, action) => {
        state.status = 'idle';
      })
      .addCase(getTokenFromRefreshAsync.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(getTokenFromRefreshAsync.fulfilled, (state, action) => {
        state.status = 'idle';
        state.access_token = action.payload.access_token;
        let exp = new Date()
        exp.setTime(new Date().getTime() + 1000 * action.payload.expires_in);
        state.access_token_expiration_date = exp.toString();
        state.refresh_token = action.payload.refresh_token;
      })
      .addCase(getTokenFromRefreshAsync.rejected, (state, action) => {
        state.status = 'idle';
      })
      .addCase(getUserInfoAsync.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(getUserInfoAsync.fulfilled, (state, action) => {
        state.status = 'idle';
        state.user_info = action.payload;
      })
      .addCase(getUserInfoAsync.rejected, (state, action) => {
        state.status = 'idle';
      });
  },
});

export const selectLogin = (state: RootState) => state.token;

export default loginSlice.reducer;
