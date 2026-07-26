import { combineReducers } from 'redux';
import { persistStore, persistReducer } from 'redux-persist';
// Point at redux-persist's ESM build explicitly: it ships no `exports` map, and
// its CJS entry (`lib/storage`) exposes the storage object only under `.default`.
// Since the Vite 8 upgrade, default imports are ES-spec compliant and no longer
// auto-unwrap a CJS `.default`, so importing the ESM build gives the object directly.
import storage from 'redux-persist/es/storage';
import { configureStore, ThunkAction, Action } from '@reduxjs/toolkit';

import drawerOpenReducer from '../features/frame/drawerOpenSlice';
import loginReducer from '../features/login/loginSlice';
import userSettingsReducer from 'src/features/settings/userSettingsSlice';

const persistConfig = {
  key: 'root',
  storage,
  /**
   * List of global states that should not be persisted accross sessions.
   *
   * For instance the states that are not related to the users accounts can
   * be listed here.
   */
  blacklist: ['stats'],
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
    }),
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
