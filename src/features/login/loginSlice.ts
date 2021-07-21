import { createAsyncThunk, createSlice, PayloadAction } from '@reduxjs/toolkit';
import { RootState } from '../../app/store';
import { fetchAuthorization, fetchLogin, fetchToken, fetchTokenFromRefresh } from './loginAPI';

export interface LoginState {
  logged: string;
  code: string;
  token: string;
  refresh_token: string;
  status: 'idle' | 'loading' | 'failed';
}

const initialState: LoginState = {
  logged: 'false',
  code: '',
  token: '',
  refresh_token: '',
  status: 'idle',
};

export const getTokenAsync = createAsyncThunk(
  'login/fetchToken',
  async ({ code, client_id, client_secret }: any) => {
    const response = await fetchToken(code, client_id, client_secret);
    return response.data;
  }
);

export const getTokenFromRefreshAsync = createAsyncThunk(
  'login/fetchTokenFromRefresh',
  async ({ refresh_token, client_id, client_secret }: any) => {
    const response = await fetchTokenFromRefresh(refresh_token, client_id, client_secret);
    return response.data;
  }
);

export const getAuthorizationAsync = createAsyncThunk(
  'login/fetchAuthorization',
  async ({ client_id, state }: any) => {
    const response = await fetchAuthorization(client_id, state);
    return response.data;
  }
);

export const getLoginAsync = createAsyncThunk(
  'login/fetchLogin',
  async ({ username, password }: any) => {
    const response = await fetchLogin(username, password);
    return response.data;
  }
);

export const loginSlice = createSlice({
  name: 'login',
  initialState,
  reducers: {
    getToken: (state, action: PayloadAction<string>) => {
      state.token = JSON.parse(action.payload).access_token;
      state.refresh_token = JSON.parse(action.payload).refresh_token;
    },
    getTokenFromRefresh: (state, action: PayloadAction<string>) => {
      state.token = JSON.parse(action.payload).access_token;
      state.refresh_token = JSON.parse(action.payload).refresh_token;
    },
    getAuthorization: (state, action: PayloadAction<string>) => {
      state.code = action.payload;
    },
    getLogin: (state, action: PayloadAction<string>) => {
      state.logged = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(getTokenAsync.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(getTokenAsync.fulfilled, (state, action) => {
        state.status = 'idle';
        state.token = action.payload.access_token;
        state.refresh_token = action.payload.refresh_token;
      })
      .addCase(getTokenFromRefreshAsync.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(getTokenFromRefreshAsync.fulfilled, (state, action) => {
        state.status = 'idle';
        state.token = action.payload.access_token;
        state.refresh_token = action.payload.refresh_token;
      })
      .addCase(getAuthorizationAsync.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(getAuthorizationAsync.fulfilled, (state, action) => {
        state.status = 'idle';
        state.code = action.payload;
      })
      .addCase(getLoginAsync.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(getLoginAsync.fulfilled, (state, action) => {
        state.status = 'idle';
        state.logged = action.payload;
      });
  },
});

export const { getToken } = loginSlice.actions;

export const selectLogin = (state: RootState) => state.token;

export default loginSlice.reducer;
