import { combineReducers } from 'redux';
import { persistStore, persistReducer } from 'redux-persist';
import storage from 'redux-persist/lib/storage';
import { configureStore, ThunkAction, Action } from '@reduxjs/toolkit';

import drawerOpenReducer from '../features/frame/drawerOpenSlice';
import loginReducer from '../features/login/loginSlice';
import loginSuccessfulListener from 'src/features/login/loginSuccessfulListener';
import userSettingsReducer from 'src/features/settings/userSettingsSlice';

const persistConfig = {
  key: 'root',
  storage,
};
const rootReducer = combineReducers({
  drawerOpen: drawerOpenReducer,
  token: loginReducer,
  settings: userSettingsReducer,
});

const persistedReducer = persistReducer(persistConfig, rootReducer);

export const store = configureStore({
  reducer: persistedReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST'],
      },
    }).prepend(loginSuccessfulListener.middleware),
});

export const persistor = persistStore(store);

export type AppDispatch = typeof store.dispatch;
export type RootState = ReturnType<typeof store.getState>;
export type AppThunk<ReturnType = void> = ThunkAction<
  ReturnType,
  RootState,
  unknown,
  Action<string>
>;
