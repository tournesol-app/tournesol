import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import { RootState } from 'src/app/store';
import { TournesolUserSettings, UsersService } from 'src/services/openapi';

export const userSettingsInitialState: {
  settings: TournesolUserSettings;
  loaded?: boolean;
} = {
  settings: {},
};

export const fetchUserSettings = createAsyncThunk(
  'settings/fetchUserSettings',
  async (): Promise<TournesolUserSettings> => {
    return await UsersService.usersMeSettingsRetrieve();
  }
);

export const userSettingsSlice = createSlice({
  name: 'settings',
  initialState: userSettingsInitialState,
  reducers: {
    // Clear all user's settings.
    clearSettings: (state) => {
      state.settings = {};
      state.loaded = false;
    },
    // Replace all user's settings of all polls by new ones.
    replaceSettings: (state, action) => {
      state.settings = action.payload;
      state.loaded = true;
    },
    // Apply a partial settings update (e.g. from a PATCH response).
    mergeSettings: (state, action) => {
      const payload: TournesolUserSettings = action.payload ?? {};
      (Object.keys(payload) as (keyof TournesolUserSettings)[]).forEach(
        (scope) => {
          state.settings[scope] = {
            ...state.settings[scope],
            ...payload[scope],
          } as TournesolUserSettings[typeof scope];
        }
      );
      state.loaded = true;
    },
  },
  extraReducers: (builder) => {
    // Replace all user's settings of all polls by new ones.
    builder.addCase(fetchUserSettings.fulfilled, (state, action) => {
      state.settings = action.payload;
      state.loaded = true;
    });
    builder.addCase(fetchUserSettings.rejected, (state) => {
      state.loaded = true;
    });
  },
});

export const selectSettings = (state: RootState) => state.settings;

export const { clearSettings, replaceSettings, mergeSettings } =
  userSettingsSlice.actions;

export default userSettingsSlice.reducer;
