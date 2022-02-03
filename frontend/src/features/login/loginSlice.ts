import { createAsyncThunk, createSlice, PayloadAction } from '@reduxjs/toolkit';
import { RootState } from '../../app/store';
import { LoginState } from './LoginState.model';
import { fetchToken, fetchTokenFromRefresh } from './loginAPI';

export const initialState: LoginState = {
  status: 'idle',
};

export const getTokenAsync = createAsyncThunk(
  'login/fetchToken',
  async ({ username, password }: { username: string; password: string }) => {
    const response = await fetchToken({ username, password });
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
    logout: (state: LoginState) => {
      state.status = 'idle';
      state.access_token = undefined;
      state.refresh_token = undefined;
      state.access_token_expiration_date = undefined;
      state.username = undefined;
    },
    updateUsername: (
      state: LoginState,
      action: PayloadAction<{ username: string }>
    ) => {
      state.username = action.payload.username;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(getTokenAsync.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(getTokenAsync.fulfilled, (state, action) => {
        state.status = 'idle';
        state.access_token = action.payload.access_token;
        const exp = new Date();
        exp.setTime(new Date().getTime() + 1000 * action.payload.expires_in);
        state.access_token_expiration_date = exp.toString();
        state.refresh_token = action.payload.refresh_token;
        state.username = action.payload.username;
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
        const exp = new Date();
        exp.setTime(new Date().getTime() + 1000 * action.payload.expires_in);
        state.access_token_expiration_date = exp.toString();
        state.refresh_token = action.payload.refresh_token;
      })
      .addCase(getTokenFromRefreshAsync.rejected, (state) => {
        state.status = 'idle';
        console.log(
          'attempt at refreshing access_token failed, erasing access, refresh and id tokens'
        );
        state.access_token = undefined;
        state.refresh_token = undefined;
      });
  },
});

export const selectLogin = (state: RootState) => state.token;
export const { logout, updateUsername } = loginSlice.actions;

export default loginSlice.reducer;
