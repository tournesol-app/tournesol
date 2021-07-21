import { configureStore, ThunkAction, Action } from '@reduxjs/toolkit';
import drawerOpenReducer from '../features/frame/drawerOpenSlice';
import loginReducer from '../features/login/loginSlice';

export const store = configureStore({
  reducer: {
    drawerOpen: drawerOpenReducer,
    token: loginReducer,
  },
});

export type AppDispatch = typeof store.dispatch;
export type RootState = ReturnType<typeof store.getState>;
export type AppThunk<ReturnType = void> = ThunkAction<
  ReturnType,
  RootState,
  unknown,
  Action<string>
>;
