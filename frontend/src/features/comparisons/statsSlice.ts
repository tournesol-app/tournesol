import { RootState } from '../../app/store';
import { createSlice, PayloadAction } from '@reduxjs/toolkit'; //createAsyncThunk

import { PollStats } from 'src/utils/types';
import { DEFAULT_POLL_STATS } from 'src/utils/api/stats';

export const initialState: PollStats = DEFAULT_POLL_STATS;

// export const fetchStats = createAsyncThunk('/stats/', async (): Promise<>)

export const statsSlice = createSlice({
  name: 'comparison',
  initialState,
  reducers: {
    fetchStatsData: (state: PollStats, action: PayloadAction<PollStats>) => {
      console.log('PollStats Action Received:', action);
      state.userCount = action.payload.userCount;
      state.lastMonthUserCount = action.payload.lastMonthUserCount;
      state.comparedEntityCount = action.payload.comparedEntityCount;
      state.lastMonthComparedEntityCount =
        action.payload.lastMonthComparedEntityCount;
      state.comparisonCount = action.payload.comparisonCount;
      state.lastThirtyDaysComparisonCount =
        action.payload.lastThirtyDaysComparisonCount;
      state.currentWeekComparisonCount =
        action.payload.currentWeekComparisonCount;

      //   console.log('Added data using redux:', state.userCount);
    },
  },
});

export const selectStats = (state: RootState) => state.statsData;
export const { fetchStatsData } = statsSlice.actions;
export default statsSlice.reducer;
