import { createSlice } from '@reduxjs/toolkit';
import { RootState } from '../../app/store';

import { theme } from 'src/theme';

export const drawerOpenSlice = createSlice({
  name: 'drawerOpen',
  initialState: {
    value: window.innerWidth >= theme.breakpoints.values['sm'],
  },
  reducers: {
    openDrawer: (state) => {
      state.value = true;
    },
    closeDrawer: (state) => {
      state.value = false;
    },
  },
});

export const { openDrawer, closeDrawer } = drawerOpenSlice.actions;

export const selectFrame = (state: RootState) => state.drawerOpen.value;

export default drawerOpenSlice.reducer;
