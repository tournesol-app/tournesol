import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import { RootState } from 'src/app/store';

import { Statistics, StatsService } from 'src/services/openapi';

const initialState: Statistics = {
  active_users: {
    total: 0,
    joined_last_month: 0,
    joined_last_30_days: 0,
  },
  polls: [],
};

export const fetchStats = createAsyncThunk(
  'stats/fetchStats',
  async (): Promise<Statistics> => {
    return await StatsService.statsRetrieve();
  }
);

const statsSlice = createSlice({
  name: 'stats',
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    // Refresh all statistics.
    builder.addCase(fetchStats.fulfilled, (state, action) => {
      state.active_users = action.payload.active_users;
      state.polls = action.payload.polls;
    });
  },
});

export const selectStats = (state: RootState) => state.stats;

export default statsSlice.reducer;
