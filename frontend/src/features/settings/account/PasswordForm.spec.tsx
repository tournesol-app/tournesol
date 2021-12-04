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

import PasswordForm from './PasswordForm';
import { initialState } from '../../login/loginSlice';
import { LoginState } from '../../login/LoginState.model';
import { OpenAPI } from 'src/services/openapi';

interface MockState {
  token: LoginState;
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

describe('change password feature', () => {
  const mockStore: MockStoreCreator<
    MockState,
    ThunkDispatch<LoginState, undefined, AnyAction>
  > = configureStore([thunk]);

  const api_url = process.env.REACT_APP_API_URL;
  OpenAPI.BASE = api_url;

  fetchMock
    .mock(
      {
        name: 'success',
        url: api_url + '/accounts/change-password/',
        method: 'POST',
        functionMatcher: (_, { body }) => {
          return (
            body ===
            '{"old_password":"success","password":"new_passwd","password_confirm":"new_passwd"}'
          );
        },
      },
      {
        status: 200,
        body: {
          detail: 'Password changed successfully',
        },
      },
      { sendAsJson: true }
    )
    .mock(
      {
        name: 'success_malformed',
        url: api_url + '/accounts/change-password/',
        method: 'POST',
        functionMatcher: (_, { body }) => {
          return (
            body ===
            '{"old_password":"success_malformed","password":"new_passwd","password_confirm":"new_passwd"}'
          );
        },
      },
      {
        status: 200,
        body: {
          random_key: 'random message',
        },
      },
      { sendAsJson: true }
    )
    .mock(
      {
        name: 'errors',
        url: api_url + '/accounts/change-password/',
        method: 'POST',
        functionMatcher: (_, { body }) => {
          return (
            body ===
            '{"old_password":"errors","password":"too_short","password_confirm":"too_short"}'
          );
        },
      },
      {
        status: 400,
        body: {
          old_password: ['Old password is not correct'],
          password: [
            'This password is too short. It must contain at least 8 characters.',
          ],
        },
      },
      { sendAsJson: true }
    );

  const component = ({ store }: { store: MockStoreEnhanced<MockState> }) =>
    render(
      <Provider store={store}>
        <SnackbarProvider maxSnack={6} autoHideDuration={6000}>
          <PasswordForm />
        </SnackbarProvider>
      </Provider>
    );

  const setup = () => {
    const state = { token: initialState };
    const store = mockStore(state);
    const rendered = component({ store: store });

    const oldPassword = screen.getByTestId('old_password');
    const password = screen.getByTestId('password');
    const passwordConfirm = screen.getByTestId('password_confirm');
    const submit = screen.getByText(/UPDATE PASSWORD/i);

    return {
      oldPassword,
      password,
      passwordConfirm,
      submit,
      rendered,
    };
  };

  it('handles successful password updates', async () => {
    const { oldPassword, password, passwordConfirm, submit } = setup();

    fireEvent.change(oldPassword, { target: { value: 'success' } });
    fireEvent.change(password, { target: { value: 'new_passwd' } });
    fireEvent.change(passwordConfirm, { target: { value: 'new_passwd' } });
    expect(submit).toBeEnabled();

    await act(async () => {
      fireEvent.click(submit);
    });

    expect(oldPassword).toHaveValue('');
    expect(password).toHaveValue('');
    expect(passwordConfirm).toHaveValue('');
    expect(submit).toBeEnabled();
    expect(mockEnqueueSnackbar).toBeCalledTimes(1);
    expect(mockEnqueueSnackbar).toBeCalledWith(
      'Password changed successfully',
      {
        variant: 'success',
      }
    );
  });

  it('handles success body responses containing no detail key', async () => {
    const { oldPassword, password, passwordConfirm, submit } = setup();

    fireEvent.change(oldPassword, { target: { value: 'success_malformed' } });
    fireEvent.change(password, { target: { value: 'new_passwd' } });
    fireEvent.change(passwordConfirm, { target: { value: 'new_passwd' } });
    expect(submit).toBeEnabled();

    await act(async () => {
      fireEvent.click(submit);
    });

    expect(oldPassword).toHaveValue('');
    expect(password).toHaveValue('');
    expect(passwordConfirm).toHaveValue('');
    expect(submit).toBeEnabled();
    expect(mockEnqueueSnackbar).toBeCalledTimes(1);
    expect(mockEnqueueSnackbar).toBeCalledWith(
      'Password changed successfully',
      {
        variant: 'success',
      }
    );
  });

  it('handles bad requests and displays all error messages', async () => {
    const { oldPassword, password, passwordConfirm, submit } = setup();

    fireEvent.change(oldPassword, { target: { value: 'errors' } });
    fireEvent.change(password, { target: { value: 'too_short' } });
    fireEvent.change(passwordConfirm, { target: { value: 'too_short' } });
    expect(submit).toBeEnabled();

    await act(async () => {
      fireEvent.click(submit);
    });

    expect(oldPassword).toHaveValue('errors');
    expect(password).toHaveValue('too_short');
    expect(passwordConfirm).toHaveValue('too_short');
    expect(submit).toBeEnabled();
    expect(mockEnqueueSnackbar).toBeCalledTimes(2);
    expect(mockEnqueueSnackbar).toBeCalledWith('Old password is not correct', {
      variant: 'error',
    });
    expect(mockEnqueueSnackbar).toBeCalledWith(
      'This password is too short. It must contain at least 8 characters.',
      {
        variant: 'error',
      }
    );
  });
});
