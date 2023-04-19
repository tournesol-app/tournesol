import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import { RootState } from 'src/app/store';
import { TournesolUserSettings, UsersService } from 'src/services/openapi';

export const userSettingsInitialState: { settings: TournesolUserSettings } = {
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
    },
    // Replace all user's settings of all polls by new ones.
    replaceSettings: (state, action) => {
      state.settings = action.payload;
    },
  },
  extraReducers: (builder) => {
    // Replace all user's settings of all polls by new ones.
    builder.addCase(fetchUserSettings.fulfilled, (state, action) => {
      state.settings = action.payload;
    });
  },
});

export const selectSettings = (state: RootState) => state.settings;

export const { clearSettings, replaceSettings } = userSettingsSlice.actions;

export default userSettingsSlice.reducer;
