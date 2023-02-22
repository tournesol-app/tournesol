import { createSlice } from '@reduxjs/toolkit';
import { TournesolUserSettings } from 'src/services/openapi';

export const userSettingsInitialState: { settings: TournesolUserSettings } = {
  settings: {},
};

export const userSettingsSlice = createSlice({
  name: 'settings',
  initialState: userSettingsInitialState,
  reducers: {
    /**
     * Replace all user's settings by new ones.
     */
    replaceUserSettings: (state, action) => {
      state.settings = action.payload;
    },
  },
});

export const { replaceUserSettings } = userSettingsSlice.actions;

export default userSettingsSlice.reducer;
