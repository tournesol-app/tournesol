import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import { RootState } from '../../app/store';
import { fetchAuthorization, fetchLogin, fetchToken, fetchTokenFromRefresh } from './loginAPI';

export interface LoginState {
  logged: boolean;
  code: string;
  access_token: string;
  refresh_token: string;
  id_token: string;
  status: 'idle' | 'loading' | 'failed';
}

const initialState: LoginState = {
  logged: false,
  code: '',
  access_token: '',
  refresh_token: '',
  id_token: '',
  status: 'idle',
};

export const getLoginAsync = createAsyncThunk(
  'login/fetchLogin',
  async ({username, password}: {username: string, password: string}) => {
    const response = await fetchLogin(username, password);
    return JSON.stringify(response.data);
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
        state.logged = JSON.parse(action.payload);
      })
      .addCase(getAuthorizationAsync.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(getAuthorizationAsync.fulfilled, (state, action) => {
        state.status = 'idle';
        state.code = action.payload;
      })
      .addCase(getTokenAsync.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(getTokenAsync.fulfilled, (state, action) => {
        state.status = 'idle';
        state.access_token = action.payload.access_token?action.payload.access_token:'';
        state.refresh_token = action.payload.refresh_token?action.payload.refresh_token:'';
        state.id_token = action.payload.id_token?action.payload.id_token:'';
      })
      .addCase(getTokenFromRefreshAsync.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(getTokenFromRefreshAsync.fulfilled, (state, action) => {
        state.status = 'idle';
        state.access_token = action.payload.access_token?action.payload.access_token:'';
        state.refresh_token = action.payload.refresh_token?action.payload.refresh_token:'';
      });
  },
});

export const selectLogin = (state: RootState) => state.token;

export default loginSlice.reducer;
