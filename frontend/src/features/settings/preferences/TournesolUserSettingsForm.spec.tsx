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
import { render, screen, fireEvent } from '@testing-library/react';
import { SnackbarProvider } from 'notistack';

import { LoginState } from 'src/features/login/LoginState.model';
import { initialState } from 'src/features/login/loginSlice';
import {
  ComparisonUi_weeklyCollectiveGoalDisplayEnum,
  Notifications_langEnum,
  OpenAPI,
  Recommendations_defaultDateEnum,
  TournesolUserSettings,
} from 'src/services/openapi';

import TournesolUserSettingsForm from './TournesolUserSettingsForm';

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

describe('GenericPollUserSettingsForm', () => {
  const mockStore: MockStoreCreator<
    MockState,
    ThunkDispatch<LoginState, undefined, AnyAction>
  > = configureStore([thunk]);

  const api_url = process.env.REACT_APP_API_URL || '';
  OpenAPI.BASE = api_url;

  const INIT_AUTO_REMOVAL_STORE = 2;

  fetchMock
    .mock(
      {
        name: 'success_patch',
        url: api_url + '/users/me/settings/',
        method: 'PATCH',
        functionMatcher: (_, { body }) => {
          if (!body) {
            return false;
          }

          const bodyContent = body.toString();
          return bodyContent.includes('"rate_later__auto_remove":16');
        },
      },
      {
        status: 200,
        body: {
          videos: {
            rate_later__auto_remove: 16,
            comparison_ui__weekly_collective_goal_display: 'NEVER',
            recommendations__default_unsafe: true,
          },
          general: {
            notifications_email__research: true,
            notifications_email__new_features: true,
          },
        },
      },
      { sendAsJson: true }
    )
    .mock(
      {
        name: 'errors_patch',
        url: api_url + '/users/me/settings/',
        method: 'PATCH',
        functionMatcher: (_, { body }) => {
          if (!body) {
            return false;
          }

          const bodyContent = body.toString();
          return bodyContent.includes('"rate_later__auto_remove":-1');
        },
      },
      {
        status: 400,
        body: {
          videos: {
            rate_later__auto_remove: ['This parameter cannot be lower than 1.'],
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
                    <TournesolUserSettingsForm />
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
  const useSelectorSpy = jest.spyOn(reactRedux, 'useSelector');

  const setup = async () => {
    const state = {
      token: initialState,
      settings: {
        videos: {
          // Here we don't define all the settings so we can ensure the form
          // behaves correctly when initialized with undefined settings.
          rate_later__auto_remove: INIT_AUTO_REMOVAL_STORE,
        },
      },
    };
    const store = mockStore(state);
    storeDispatchSpy = jest.spyOn(store, 'dispatch');

    const rendered = await component({ store: store });

    const notificationsEmailResearch = screen.getByTestId(
      'notifications_email__research'
    );
    const notificationsEmailNewFeatures = screen.getByTestId(
      'notifications_email__new_features'
    );
    const notificationsLang = screen.getByTestId('notifications__lang');

    const compUiWeeklyColGoalDisplay = screen.getByTestId(
      'videos_weekly_collective_goal_display'
    );
    const rateLaterAutoRemove = screen.getByTestId(
      'videos_rate_later__auto_remove'
    );
    const recommendationsDefaultDate = screen.getByTestId(
      'videos_recommendations__default_date'
    );
    const recommendationsDefaultUnsafe = screen.getByTestId(
      'videos_recommendations__default_unsafe'
    );

    const submit = screen.getByRole('button', { name: /update/i });

    return {
      compUiWeeklyColGoalDisplay,
      notificationsEmailResearch,
      notificationsEmailNewFeatures,
      notificationsLang,
      rateLaterAutoRemove,
      recommendationsDefaultDate,
      recommendationsDefaultUnsafe,
      rendered,
      storeDispatchSpy,
      submit,
    };
  };

  beforeEach(() => {
    useSelectorSpy.mockClear();
    // The value of `rate_later__auto_remove` should be different than the one
    // used to initialize the store, to make the tests relevant.
    useSelectorSpy.mockReturnValue({
      settings: { videos: { rate_later__auto_remove: 8 } },
    });
  });

  afterEach(() => {
    storeDispatchSpy.mockClear();
  });

  describe('Success', () => {
    it('displays the defined values after a submit', async () => {
      const {
        compUiWeeklyColGoalDisplay,
        notificationsEmailResearch,
        notificationsEmailNewFeatures,
        notificationsLang,
        rateLaterAutoRemove,
        recommendationsDefaultDate,
        recommendationsDefaultUnsafe,
        submit,
      } = await setup();

      expect(rateLaterAutoRemove).toHaveValue(8);

      // Here we check the default values used when the settings are not yet
      // defined by the user. The email notifications should always be false
      // by default.
      expect(notificationsLang).toHaveValue(Notifications_langEnum.FRENCH);
      expect(notificationsEmailResearch).toHaveProperty('checked', false);
      expect(notificationsEmailNewFeatures).toHaveProperty('checked', false);

      expect(compUiWeeklyColGoalDisplay).toHaveValue(
        ComparisonUi_weeklyCollectiveGoalDisplayEnum.ALWAYS
      );
      expect(recommendationsDefaultDate).toHaveValue(
        Recommendations_defaultDateEnum.MONTH
      );
      expect(recommendationsDefaultUnsafe).toHaveProperty('checked', false);

      fireEvent.click(notificationsEmailResearch);
      fireEvent.click(notificationsEmailNewFeatures);
      fireEvent.change(rateLaterAutoRemove, { target: { value: 16 } });
      fireEvent.change(compUiWeeklyColGoalDisplay, {
        target: { value: ComparisonUi_weeklyCollectiveGoalDisplayEnum.NEVER },
      });
      fireEvent.change(recommendationsDefaultDate, {
        target: { value: Recommendations_defaultDateEnum.ALL_TIME },
      });
      fireEvent.click(recommendationsDefaultUnsafe);

      expect(submit).toBeEnabled();

      await act(async () => {
        fireEvent.click(submit);
      });

      expect(notificationsEmailResearch).toHaveProperty('checked', true);
      expect(notificationsEmailNewFeatures).toHaveProperty('checked', true);
      expect(rateLaterAutoRemove).toHaveValue(16);
      expect(compUiWeeklyColGoalDisplay).toHaveValue(
        ComparisonUi_weeklyCollectiveGoalDisplayEnum.NEVER
      );
      expect(recommendationsDefaultDate).toHaveValue(
        Recommendations_defaultDateEnum.ALL_TIME
      );
      expect(recommendationsDefaultUnsafe).toHaveProperty('checked', true);
      expect(submit).toBeEnabled();
    });

    it('retrieves its initial values from the Redux store', async () => {
      const { rateLaterAutoRemove } = await setup();
      expect(useSelectorSpy).toHaveBeenCalledTimes(1);
      expect(rateLaterAutoRemove).toHaveValue(8);
    });

    it("calls the store's dispatch function after a submit", async () => {
      const {
        rateLaterAutoRemove,
        recommendationsDefaultUnsafe,
        notificationsEmailResearch,
        notificationsEmailNewFeatures,
        storeDispatchSpy,
        submit,
      } = await setup();
      expect(storeDispatchSpy).toHaveBeenCalledTimes(0);

      fireEvent.click(notificationsEmailResearch);
      fireEvent.click(notificationsEmailNewFeatures);
      fireEvent.change(rateLaterAutoRemove, { target: { value: 16 } });
      fireEvent.click(recommendationsDefaultUnsafe);

      await act(async () => {
        fireEvent.click(submit);
      });

      expect(storeDispatchSpy).toHaveBeenCalledTimes(1);
      expect(storeDispatchSpy).lastCalledWith({
        type: 'settings/replaceSettings',
        payload: {
          general: {
            notifications_email__research: true,
            notifications_email__new_features: true,
          },
          videos: {
            comparison_ui__weekly_collective_goal_display:
              ComparisonUi_weeklyCollectiveGoalDisplayEnum.NEVER,
            rate_later__auto_remove: 16,
            recommendations__default_unsafe: true,
          },
        },
      });
    });

    it('displays a generic success message with notistack', async () => {
      const { rateLaterAutoRemove, submit } = await setup();

      fireEvent.change(rateLaterAutoRemove, { target: { value: 16 } });

      await act(async () => {
        fireEvent.click(submit);
      });

      expect(mockEnqueueSnackbar).toBeCalledTimes(1);
      expect(mockEnqueueSnackbar).toBeCalledWith(
        expect.stringMatching(/successfully/i),
        {
          variant: 'success',
        }
      );
    });
  });

  describe('Errors', () => {
    it('displays the defined values after a submit', async () => {
      const { rateLaterAutoRemove, submit } = await setup();

      fireEvent.change(rateLaterAutoRemove, { target: { value: -1 } });
      expect(submit).toBeEnabled();

      await act(async () => {
        fireEvent.click(submit);
      });

      expect(rateLaterAutoRemove).toHaveValue(-1);
      expect(submit).toBeEnabled();
    });

    it("doesn't call the store's dispatch function after a submit", async () => {
      const { rateLaterAutoRemove, storeDispatchSpy, submit } = await setup();

      fireEvent.change(rateLaterAutoRemove, { target: { value: -1 } });

      await act(async () => {
        fireEvent.click(submit);
      });

      expect(storeDispatchSpy).toBeCalledTimes(0);
    });

    it('displays a generic error message with notistack', async () => {
      const { rateLaterAutoRemove, submit } = await setup();

      fireEvent.change(rateLaterAutoRemove, { target: { value: -1 } });

      await act(async () => {
        fireEvent.click(submit);
      });

      expect(mockEnqueueSnackbar).toBeCalledTimes(1);
      expect(mockEnqueueSnackbar).toBeCalledWith(
        'pollUserSettingsForm.errorOccurredDuringPreferencesUpdate',
        {
          variant: 'error',
        }
      );
    });

    it('displays the error messages of each field', async () => {
      const { rateLaterAutoRemove, submit } = await setup();

      fireEvent.change(rateLaterAutoRemove, { target: { value: -1 } });

      expect(
        screen.queryByText(/this parameter cannot be lower than 1./i)
      ).not.toBeInTheDocument();

      await act(async () => {
        fireEvent.click(submit);
      });

      expect(
        screen.getByText(/this parameter cannot be lower than 1./i)
      ).toBeInTheDocument();
    });
  });
});
