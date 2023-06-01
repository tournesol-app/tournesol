import React from 'react';
import { MemoryRouter, Route, Switch } from 'react-router-dom';

import fetchMock from 'fetch-mock-jest';
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

const mockEnqueueSnackbar = jest.fn();

jest.mock('notistack', () => ({
  ...jest.requireActual('notistack'),
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

  const api_url = process.env.REACT_APP_API_URL || '';
  OpenAPI.BASE = api_url;

  // The values used by the store and the API are different to ensure the form
  // is initialized with the correct source of information.
  const INIT_AUTO_REMOVAL_API = 8;
  const INIT_AUTO_REMOVAL_STORE = 0;

  fetchMock.mock(
    {
      name: 'success_get',
      url: api_url + '/users/me/settings/',
      method: 'GET',
      functionMatcher: () => true,
    },
    {
      status: 200,
      body: {
        videos: {
          rate_later__auto_remove: INIT_AUTO_REMOVAL_API,
          weekly_collective_goal_display:
            ComparisonUi_weeklyCollectiveGoalDisplayEnum.NEVER,
        },
      },
    },
    { sendAsJson: true }
  );

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

  let storeDispatchSpy: jest.SpyInstance;

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
    storeDispatchSpy = jest.spyOn(store, 'dispatch');
    const rendered = await component({ store: store });

    return {
      rendered,
      storeDispatchSpy,
    };
  };

  afterEach(() => {
    storeDispatchSpy.mockClear();
  });

  it('retrieves the preferences from the API and dispatch them', async () => {
    const { storeDispatchSpy } = await setup();
    expect(storeDispatchSpy).toHaveBeenCalledTimes(1);

    expect(storeDispatchSpy).toBeCalledWith({
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
