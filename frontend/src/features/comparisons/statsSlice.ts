import { RootState } from '../../app/store';
import { createSlice, PayloadAction } from '@reduxjs/toolkit';

import { PollStats } from 'src/utils/types';
import { DEFAULT_POLL_STATS } from 'src/utils/api/stats';

const initialState: PollStats = DEFAULT_POLL_STATS;

const statsSlice = createSlice({
  name: 'comparison',
  initialState,
  reducers: {
    fetchStatsData: (state: PollStats, action: PayloadAction<PollStats>) => {
      console.log('redux statsSlice pollStats:', action.payload);
      state.userCount = action.payload.userCount;
      state.lastMonthUserCount = action.payload.lastMonthUserCount;
      state.lastThirtyDaysUserCount = action.payload.lastThirtyDaysUserCount;
      state.comparedEntityCount = action.payload.comparedEntityCount;
      state.lastMonthComparedEntityCount =
        action.payload.lastMonthComparedEntityCount;
      state.lastThirtyDaysComparedEntityCount =
        action.payload.lastThirtyDaysComparedEntityCount;
      state.comparisonCount = action.payload.comparisonCount;
      state.lastMonthComparisonCount = action.payload.lastMonthComparisonCount;
      state.lastThirtyDaysComparisonCount =
        action.payload.lastThirtyDaysComparisonCount;
      state.currentWeekComparisonCount =
        action.payload.currentWeekComparisonCount;
    },
  },
});

export const selectStats = (state: RootState) => state.statsData;
export const { fetchStatsData } = statsSlice.actions;
export default statsSlice.reducer;
