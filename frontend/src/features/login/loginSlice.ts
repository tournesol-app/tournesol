import { createAsyncThunk, createSlice, PayloadAction } from '@reduxjs/toolkit';
import { RootState } from '../../app/store';
import { LoginState } from './LoginState.model';
import {
  fetchToken,
  fetchTokenFromRefresh,
  RefreshedTokenPayload,
} from './loginAPI';

export const initialState: LoginState = {
  status: 'idle',
};

const TOKEN_MIN_VALIDITY_MS = 600000;

const pendingRefresh: Record<
  string,
  Promise<{ data: RefreshedTokenPayload }>
> = {};

const needsRefresh = (login: LoginState) => {
  if (!login.refresh_token) {
    return false;
  }
  if (!login.access_token || !login.access_token_expiration_date) {
    return true;
  }
  const expirationDate = new Date(login.access_token_expiration_date);
  const validityExpected = new Date(
    new Date().getTime() + TOKEN_MIN_VALIDITY_MS
  );
  return expirationDate < validityExpected;
};

export const getTokenAsync = createAsyncThunk(
  'login/fetchToken',
  async ({ username, password }: { username: string; password: string }) => {
    const response = await fetchToken({ username, password });
    return response.data;
  }
);

export const getTokenFromRefreshAsync = createAsyncThunk<
  RefreshedTokenPayload,
  undefined,
  { state: RootState }
>(
  'login/fetchTokenFromRefresh',
  async (_, { getState }) => {
    const refreshToken = getState().token.refresh_token ?? '';
    if (!pendingRefresh[refreshToken]) {
      pendingRefresh[refreshToken] = fetchTokenFromRefresh(refreshToken);
    }
    const response = await pendingRefresh[refreshToken];
    return response.data;
  },
  {
    condition: (_, { getState }) => {
      const loginState = getState().token;
      if (!needsRefresh(loginState)) {
        return false;
      }
    },
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
      state.backPath = undefined;
      state.backParams = undefined;
    },
    updateUsername: (
      state: LoginState,
      action: PayloadAction<{ username: string }>
    ) => {
      state.username = action.payload.username;
    },
    /**
     * Save the given path and URL parameters to allow the back buttons to
     * return to the desired location.
     */
    updateBackNagivation: (
      state: LoginState,
      action: PayloadAction<{ backPath: string; backParams: string }>
    ) => {
      state.backPath = action.payload.backPath;
      state.backParams = action.payload.backParams;
    },
    clearBackNavigation: (state: LoginState) => {
      state.backPath = undefined;
      state.backParams = undefined;
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
        state.username = action.payload.username;
      })
      .addCase(getTokenFromRefreshAsync.rejected, (state) => {
        state.status = 'idle';
        console.log(
          'attempt at refreshing access_token failed, erasing access, refresh and id tokens'
        );
        state.access_token = undefined;
        state.refresh_token = undefined;
        state.access_token_expiration_date = undefined;
      });
  },
});

export const selectLogin = (state: RootState) => state.token;
export const {
  clearBackNavigation,
  logout,
  updateUsername,
  updateBackNagivation,
} = loginSlice.actions;

export default loginSlice.reducer;
