import { createAsyncThunk, createSlice, PayloadAction } from '@reduxjs/toolkit';
import { RootState } from 'src/app/store';
import { fetchLogin } from './wikiLoginAPI';
import { WikiLoginState } from './WikiLoginState.model';

export const initialState: WikiLoginState = {
  logged: false,
  status: 'idle',
};

export const getLoginAsync = createAsyncThunk(
  'login/fetchLogin',
  async ({ username, password }: { username: string; password: string }) => {
    await fetchLogin(username, password);
  }
);

export const wikiLoginSlice = createSlice({
  name: 'wikiLogin',
  initialState,
  reducers: {
    logout: (state: WikiLoginState) => {
      state.status = 'idle';
      state.username = undefined;
    },
    updateUsername: (
      state: WikiLoginState,
      action: PayloadAction<{ username: string }>
    ) => {
      state.username = action.payload.username;
    },
  },
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
      });
  },
});

export const selectWikiLogin = (state: RootState) => state.wikiLogin;
export const { logout, updateUsername } = wikiLoginSlice.actions;

export default wikiLoginSlice.reducer;
