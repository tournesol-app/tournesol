import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
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
  reducers: {},
  extraReducers: (builder) => {
    /**
     * Replace all user's settings by new ones.
     */
    builder.addCase(fetchUserSettings.fulfilled, (state, action) => {
      state.settings = action.payload;
    });
  },
});

export default userSettingsSlice.reducer;
