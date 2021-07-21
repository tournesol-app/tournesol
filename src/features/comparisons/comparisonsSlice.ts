import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import { RootState } from '../../app/store';
import { fetchComparisons } from './comparisonsAPI';

export interface ComparisonsState {
  value: string;
  status: 'idle' | 'loading' | 'failed';
}

const initialState: ComparisonsState = {
  value: '',
  status: 'idle',
};

export const getComparisonsAsync = createAsyncThunk(
  'comparisons/fetchComparisons',
  async (access_token: string) => {
    return await fetchComparisons(access_token);
  }
);

export const comparisonsSlice = createSlice({
  name: 'comparisons',
  initialState,
  reducers: {
  },
  extraReducers: (builder) => {
    builder
      .addCase(getComparisonsAsync.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(getComparisonsAsync.fulfilled, (state, action) => {
        state.status = 'idle';
        state.value = action.payload;
      })
      .addCase(getComparisonsAsync.rejected, (state, action) => {
        state.status = 'idle';
      });
  },
});

export const selectComparisons = (state: RootState) => state.comparisons;

export default comparisonsSlice.reducer;
