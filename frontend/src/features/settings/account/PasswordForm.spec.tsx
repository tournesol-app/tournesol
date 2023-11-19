import React from 'react';
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

const mockEnqueueSnackbar = vi.fn();

vi.mock('notistack', async () => ({
  ...(await vi.importActual<object>('notistack')),
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

  const api_url = import.meta.env.REACT_APP_API_URL || '';
  OpenAPI.BASE = api_url;

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
    const submit = screen.getByRole('button', { name: /update/i });

    return {
      oldPassword,
      password,
      passwordConfirm,
      submit,
      rendered,
    };
  };

  it('handles successful password updates', async () => {
    fetchMock.mockIf(
      (req) =>
        req.method == 'POST' && /accounts\/change-password/.test(req.url),
      () => ({
        init: {
          status: 200,
          headers: {
            'Content-Type': 'application/json',
          },
        },
        body: JSON.stringify({
          detail: 'Password changed successfully',
        }),
      })
    );

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
    expect(mockEnqueueSnackbar).toHaveBeenCalledTimes(1);
    expect(mockEnqueueSnackbar).toHaveBeenCalledWith(
      expect.stringMatching(/successfully/i),
      {
        variant: 'success',
      }
    );
  });

  it('handles success body responses containing no detail key', async () => {
    fetchMock.mockIf(
      (req) =>
        req.method == 'POST' && /accounts\/change-password/.test(req.url),
      () => ({
        init: {
          status: 200,
          headers: {
            'Content-Type': 'application/json',
          },
        },
        body: JSON.stringify({
          random_key: 'random message',
        }),
      })
    );

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
    expect(mockEnqueueSnackbar).toHaveBeenCalledTimes(1);
    expect(mockEnqueueSnackbar).toHaveBeenCalledWith(
      expect.stringMatching(/successfully/i),
      {
        variant: 'success',
      }
    );
  });

  it('handles bad requests and displays all error messages', async () => {
    fetchMock.mockIf(
      (req) =>
        req.method == 'POST' && /accounts\/change-password/.test(req.url),
      () => ({
        init: {
          status: 400,
          headers: {
            'Content-Type': 'application/json',
          },
        },
        body: JSON.stringify({
          old_password: ['Old password is not correct'],
          password: [
            'This password is too short. It must contain at least 8 characters.',
          ],
        }),
      })
    );

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
