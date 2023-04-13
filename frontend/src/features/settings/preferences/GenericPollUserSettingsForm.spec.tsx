import React from 'react';

import fetchMock from 'fetch-mock-jest';
import { SnackbarProvider } from 'notistack';
import { act } from 'react-dom/test-utils';
import { Provider } from 'react-redux';
import configureStore, {
  MockStoreCreator,
  MockStoreEnhanced,
} from 'redux-mock-store';
import { AnyAction } from '@reduxjs/toolkit';
import thunk, { ThunkDispatch } from 'redux-thunk';
import { render, screen, fireEvent } from '@testing-library/react';

import { LoginState } from 'src/features/login/LoginState.model';
import { initialState } from 'src/features/login/loginSlice';
import { OpenAPI, TournesolUserSettings } from 'src/services/openapi';

import GenericPollUserSettingsForm from './GenericPollUserSettingsForm';

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

  fetchMock
    .mock(
      {
        name: 'success',
        url: api_url + '/users/me/settings/',
        method: 'PATCH',
        functionMatcher: (_, { body }) => {
          return body === '{"videos":{"rate_later__auto_remove":16}}';
        },
      },
      {
        status: 200,
        body: {
          videos: {
            rate_later__auto_remove: 16,
          },
        },
      },
      { sendAsJson: true }
    )
    .mock(
      {
        name: 'errors',
        url: api_url + '/users/me/settings/',
        method: 'PATCH',
        functionMatcher: (_, { body }) => {
          return body === '{"videos":{"rate_later__auto_remove":-1}}';
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

  const component = ({ store }: { store: MockStoreEnhanced<MockState> }) =>
    render(
      <Provider store={store}>
        <SnackbarProvider maxSnack={6} autoHideDuration={6000}>
          <GenericPollUserSettingsForm pollName="videos" />
        </SnackbarProvider>
      </Provider>
    );

  let storeDispatchSpy: jest.SpyInstance;

  const setup = () => {
    const state = {
      token: initialState,
      settings: {
        videos: {
          rate_later__auto_remove: 4,
        },
      },
    };
    const store = mockStore(state);
    storeDispatchSpy = jest.spyOn(store, 'dispatch');
    const rendered = component({ store: store });

    const rateLaterAutoRemove = screen.getByTestId(
      'videos_rate_later__auto_remove'
    );
    const submit = screen.getByRole('button', { name: /update/i });

    return {
      rateLaterAutoRemove,
      rendered,
      storeDispatchSpy,
      submit,
    };
  };

  afterEach(() => {
    storeDispatchSpy.mockClear();
  });

  describe('Success', () => {
    it('displays the defined values after a submit', async () => {
      const { rateLaterAutoRemove, submit } = setup();

      expect(rateLaterAutoRemove).toHaveValue(4);
      fireEvent.change(rateLaterAutoRemove, { target: { value: 16 } });
      expect(submit).toBeEnabled();

      await act(async () => {
        fireEvent.click(submit);
      });

      expect(rateLaterAutoRemove).toHaveValue(16);
      expect(submit).toBeEnabled();
    });

    it("calls the store's dispatch function", async () => {
      const { rateLaterAutoRemove, storeDispatchSpy, submit } = setup();

      fireEvent.change(rateLaterAutoRemove, { target: { value: 16 } });

      await act(async () => {
        fireEvent.click(submit);
      });

      expect(storeDispatchSpy).toHaveBeenCalledTimes(1);
      expect(storeDispatchSpy).toBeCalledWith({
        type: 'settings/replaceSettings',
        payload: { videos: { rate_later__auto_remove: 16 } },
      });
    });

    it('displays a generic success message with notistack', async () => {
      const { rateLaterAutoRemove, submit } = setup();

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
      const { rateLaterAutoRemove, submit } = setup();

      fireEvent.change(rateLaterAutoRemove, { target: { value: -1 } });
      expect(submit).toBeEnabled();

      await act(async () => {
        fireEvent.click(submit);
      });

      expect(rateLaterAutoRemove).toHaveValue(-1);
      expect(submit).toBeEnabled();
    });

    it("doesn't call the store's dispatch function", async () => {
      const { rateLaterAutoRemove, storeDispatchSpy, submit } = setup();

      fireEvent.change(rateLaterAutoRemove, { target: { value: -1 } });

      await act(async () => {
        fireEvent.click(submit);
      });

      expect(storeDispatchSpy).toBeCalledTimes(0);
    });

    it('displays a generic error message with notistack', async () => {
      const { rateLaterAutoRemove, submit } = setup();

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
      const { rateLaterAutoRemove, submit } = setup();

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
