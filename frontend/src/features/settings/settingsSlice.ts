import { createSlice } from '@reduxjs/toolkit';
import { TournesolUserSettings } from 'src/services/openapi';

export const initialState: { settings: TournesolUserSettings } = {
  settings: {},
};

export const settingsSlice = createSlice({
  name: 'settings',
  initialState: initialState,
  reducers: {
    /**
     * Replace all user's settings by new ones.
     */
    replaceSettings: (state, action) => {
      state.settings = action.payload;
    },
  },
});

export const { replaceSettings } = settingsSlice.actions;

export default settingsSlice.reducer;
