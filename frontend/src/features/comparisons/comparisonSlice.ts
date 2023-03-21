import { RootState } from '../../app/store';
import { createSlice, PayloadAction } from '@reduxjs/toolkit';

import { PollStats } from 'src/utils/types';
import { DEFAULT_POLL_STATS } from 'src/utils/api/stats';

export const initialState: PollStats = DEFAULT_POLL_STATS;

export const comparisonSlice = createSlice({
  name: 'comparison',
  initialState,
  reducers: {
    fetchComparisonData: (
      state: PollStats,
      action: PayloadAction<PollStats>
    ) => {
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

export const selectComparison = (state: RootState) => state.comparisonData;
export const { fetchComparisonData } = comparisonSlice.actions;
export default comparisonSlice.reducer;
