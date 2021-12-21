import { createSlice } from '@reduxjs/toolkit';
import { RootState } from '../../app/store';

export const drawerOpenSlice = createSlice({
  name: 'drawerOpen',
  initialState: {
    value: true,
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
