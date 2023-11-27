import React from 'react';
import { MemoryRouter, Route, Switch } from 'react-router-dom';

import { SpyInstance } from 'vitest';
import { act } from 'react-dom/test-utils';
import * as reactRedux from 'react-redux';
import configureStore, {
  MockStoreCreator,
  MockStoreEnhanced,
} from 'redux-mock-store';
import { AnyAction } from '@reduxjs/toolkit';
import thunk, { ThunkDispatch } from 'redux-thunk';
import { render } from '@testing-library/react';
import { SnackbarProvider } from 'notistack';

import { LoginState } from 'src/features/login/LoginState.model';
import { initialState } from 'src/features/login/loginSlice';
import {
  ComparisonUi_weeklyCollectiveGoalDisplayEnum,
  OpenAPI,
  TournesolUserSettings,
} from 'src/services/openapi';

import Preferences from './Preferences';

interface MockState {
  token: LoginState;
  settings: TournesolUserSettings;
}

const mockEnqueueSnackbar = vi.fn();

vi.mock('notistack', async () => ({
  ...(await vi.importActual<object>('notistack')),
  useSnackbar: () => {
    return {
      enqueueSnackbar: mockEnqueueSnackbar,
    };
  },
}));

describe('Preferences Page', () => {
  const mockStore: MockStoreCreator<
    MockState,
    ThunkDispatch<LoginState, undefined, AnyAction>
  > = configureStore([thunk]);

  const api_url = import.meta.env.REACT_APP_API_URL || '';
  OpenAPI.BASE = api_url;

  // The values used by the store and the API are different to ensure the form
  // is initialized with the correct source of information.
  const INIT_AUTO_REMOVAL_API = 8;
  const INIT_AUTO_REMOVAL_STORE = 2;

  const component = async ({
    store,
  }: {
    store: MockStoreEnhanced<MockState>;
  }) => {
    return await act(async () => {
      Promise.resolve(
        render(
          <reactRedux.Provider store={store}>
            <SnackbarProvider maxSnack={6} autoHideDuration={6000}>
              <MemoryRouter initialEntries={['settings/preferences']}>
                <Switch>
                  <Route path="settings/preferences">
                    <Preferences />
                  </Route>
                </Switch>
              </MemoryRouter>
            </SnackbarProvider>
          </reactRedux.Provider>
        )
      );
    });
  };

  let storeDispatchSpy: SpyInstance;

  const setup = async () => {
    const state = {
      token: initialState,
      settings: {
        videos: {
          rate_later__auto_remove: INIT_AUTO_REMOVAL_STORE,
        },
      },
    };
    const store = mockStore(state);
    storeDispatchSpy = vi.spyOn(store, 'dispatch');
    await component({ store: store });

    return {
      storeDispatchSpy,
    };
  };

  afterEach(() => {
    storeDispatchSpy.mockClear();
  });

  describe("Successfully fetch the user's settings", () => {
    beforeAll(() => {
      fetchMock.mockReset();
      fetchMock.doMockIf(
        new RegExp('/users/me/settings/'),
        JSON.stringify({
          videos: {
            rate_later__auto_remove: INIT_AUTO_REMOVAL_API,
            weekly_collective_goal_display:
              ComparisonUi_weeklyCollectiveGoalDisplayEnum.NEVER,
          },
        }),
        { status: 200, headers: { 'Content-Type': 'application/json' } }
      );
    });

    it('retrieves the preferences from the API and dispatch them', async () => {
      const { storeDispatchSpy } = await setup();
      expect(storeDispatchSpy).toHaveBeenCalledTimes(1);
      expect(storeDispatchSpy).toHaveBeenCalledWith({
        type: 'settings/replaceSettings',
        payload: {
          videos: {
            rate_later__auto_remove: 8,
            weekly_collective_goal_display:
              ComparisonUi_weeklyCollectiveGoalDisplayEnum.NEVER,
          },
        },
      });
    });
  });

  describe("Error while fetching the user's settings", () => {
    beforeAll(() => {
      fetchMock.mockReset();
      fetchMock.mockIf(new RegExp('/users/me/settings/'), '{}', {
        status: 429,
      });
    });

    it('displays human readable errors', async () => {
      await setup();
      expect(mockEnqueueSnackbar).toHaveBeenCalledTimes(2);
      expect(mockEnqueueSnackbar).toHaveBeenNthCalledWith(
        1,
        'notifications.tryAgainLaterOrContactAdministrator',
        {
          variant: 'warning',
        }
      );
      expect(mockEnqueueSnackbar).toHaveBeenNthCalledWith(
        2,
        'preferences.errorOccurredWhileRetrievingPreferences',
        {
          variant: 'error',
        }
      );
    });

    it("doesn't dispatch the user's settings", async () => {
      const { storeDispatchSpy } = await setup();
      expect(storeDispatchSpy).toHaveBeenCalledTimes(0);
    });
  });
});
