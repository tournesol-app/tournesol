import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import { RootState } from '../../app/store';
import { LoginState } from './LoginState.model';
import {
  fetchLogin,
  fetchToken,
  fetchTokenFromRefresh,
  fetchUserInfo,
} from './loginAPI';

export const initialState: LoginState = {
  logged: false,
  need_refresh: false,
  status: 'idle',
};

export const getLoginAsync = createAsyncThunk(
  'login/fetchLogin',
  async ({ username, password }: { username: string; password: string }) => {
    await fetchLogin(username, password);
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
  async (access_token: string) => await fetchUserInfo(access_token)
);

export const loginSlice = createSlice({
  name: 'login',
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(getLoginAsync.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(getLoginAsync.fulfilled, (state) => {
        state.status = 'idle';
        state.logged = true;
      })
      .addCase(getLoginAsync.rejected, (state) => {
        state.status = 'idle';
        state.logged = false;
      })
      .addCase(getTokenAsync.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(getTokenAsync.fulfilled, (state, action) => {
        state.status = 'idle';
        state.access_token = action.payload.access_token;
        let exp = new Date();
        exp.setTime(new Date().getTime() + 1000 * action.payload.expires_in);
        state.access_token_expiration_date = exp.toString();
        state.refresh_token = action.payload.refresh_token;
        state.id_token = action.payload.id_token;
      })
      .addCase(getTokenAsync.rejected, (state) => {
        state.status = 'idle';
        console.log('attempt at exchanging code for token failed');
      })
      .addCase(getTokenFromRefreshAsync.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(getTokenFromRefreshAsync.fulfilled, (state, action) => {
        state.status = 'idle';
        state.access_token = action.payload.access_token;
        let exp = new Date();
        exp.setTime(new Date().getTime() + 1000 * action.payload.expires_in);
        state.access_token_expiration_date = exp.toString();
        state.refresh_token = action.payload.refresh_token;
        state.need_refresh = false;
      })
      .addCase(getTokenFromRefreshAsync.rejected, (state) => {
        state.status = 'idle';
        console.log(
          'attempt at refreshing access_token failed, erasing access, refresh and id tokens'
        );
        state.access_token = undefined;
        state.refresh_token = undefined;
        state.id_token = undefined;
        state.need_refresh = false;
      })
      .addCase(getUserInfoAsync.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(getUserInfoAsync.fulfilled, (state, action) => {
        state.status = 'idle';
        state.user_info = action.payload;
      })
      .addCase(getUserInfoAsync.rejected, (state) => {
        state.status = 'idle';
        console.log(
          'attempt at retrieving user info failed, erasing access and id tokens'
        );
        state.access_token = undefined;
        state.id_token = undefined;
        state.need_refresh = true;
      });
  },
});

export const selectLogin = (state: RootState) => state.token;

export default loginSlice.reducer;
