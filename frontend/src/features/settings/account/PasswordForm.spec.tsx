import React from 'react';

import fetchMock from 'fetch-mock-jest';
import { SnackbarProvider } from 'notistack';
import { act } from 'react-dom/test-utils';
import { Provider } from 'react-redux';
import { MemoryRouter, Route, Switch } from 'react-router-dom';
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

interface MockState {
  token: LoginState;
}

describe('change password feature', () => {
  const mockStore: MockStoreCreator<
    MockState,
    ThunkDispatch<LoginState, undefined, AnyAction>
  > = configureStore([thunk]);

  const api_url = process.env.REACT_APP_API_URL;

  fetchMock
    .mock(
      {
        name: 'success',
        url: api_url + '/accounts/change-password/',
        method: 'POST',
        functionMatcher: (_, { body }) => {
          return (
            body ===
            '{"old_password":"success","password":"new_password","password_confirm":"new_password"}'
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
            '{"old_password":"success_malformed","password":"new_password","password_confirm":"new_password"}'
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
          <MemoryRouter initialEntries={['/settings/account']}>
            <Switch>
              <Route path="/settings/account">
                <PasswordForm />
              </Route>
            </Switch>
          </MemoryRouter>
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
    return {
      oldPassword,
      password,
      passwordConfirm,
      rendered,
    };
  };

  it('handles successful password updates', async () => {
    const { oldPassword, password, passwordConfirm } = setup();

    fireEvent.change(oldPassword, { target: { value: 'success' } });
    fireEvent.change(password, { target: { value: 'new_password' } });
    fireEvent.change(passwordConfirm, { target: { value: 'new_password' } });
    await act(async () => {
      fireEvent.click(screen.getByText(/UPDATE PASSWORD/i));
    });
    expect(oldPassword).toHaveValue('');
    expect(password).toHaveValue('');
    expect(passwordConfirm).toHaveValue('');
    expect(screen.getByText('Password changed successfully')).toBeVisible();
  });

  it('handles success body responses without detail', async () => {
    const { oldPassword, password, passwordConfirm } = setup();

    fireEvent.change(oldPassword, { target: { value: 'success_malformed' } });
    fireEvent.change(password, { target: { value: 'new_password' } });
    fireEvent.change(passwordConfirm, { target: { value: 'new_password' } });
    await act(async () => {
      fireEvent.click(screen.getByText(/UPDATE PASSWORD/i));
    });
    expect(oldPassword).toHaveValue('');
    expect(password).toHaveValue('');
    expect(passwordConfirm).toHaveValue('');
    expect(screen.getByText('Password changed successfully')).toBeVisible();
  });

  it('handles and displays all error messages', async () => {
    const { oldPassword, password, passwordConfirm } = setup();

    fireEvent.change(oldPassword, { target: { value: 'errors' } });
    fireEvent.change(password, { target: { value: 'too_short' } });
    fireEvent.change(passwordConfirm, { target: { value: 'too_short' } });
    await act(async () => {
      fireEvent.click(screen.getByText(/UPDATE PASSWORD/i));
    });
    expect(oldPassword).toHaveValue('errors');
    expect(password).toHaveValue('too_short');
    expect(passwordConfirm).toHaveValue('too_short');
    expect(screen.getByText('Old password is not correct')).toBeVisible();
    expect(
      screen.getByText(
        'This password is too short. It must contain at least 8 characters.'
      )
    ).toBeVisible();
  });
});
