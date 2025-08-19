/* eslint-disable @typescript-eslint/no-explicit-any */
import React from 'react';
import { render } from '@testing-library/react';
import { act } from 'react-dom/test-utils';
import { MemoryRouter } from 'react-router-dom';
import { Route, Routes } from 'react-router-dom';
import configureStore, {
  MockStoreCreator,
  MockStoreEnhanced,
} from 'redux-mock-store';
import { Provider } from 'react-redux';
import thunk, { ThunkDispatch } from 'redux-thunk';
import { AnyAction } from '@reduxjs/toolkit';
import { SnackbarProvider } from 'notistack';
import { RootState } from 'src/app/store';
import Login from './Login';
import { LoginState } from './LoginState.model';
import {
  initialState,
  getTokenAsync,
  getTokenFromRefreshAsync,
} from './loginSlice';
import { mockAppRequests } from 'src/mockUtils';

export interface MockState {
  token: LoginState;
}

export const mockStore: MockStoreCreator<
  MockState,
  ThunkDispatch<RootState, undefined, AnyAction>
> = configureStore([thunk]);

describe('login feature', () => {
  beforeAll(() => {
    mockAppRequests();
  });

  const component = ({ store }: { store: MockStoreEnhanced<MockState> }) =>
    render(
      <Provider store={store}>
        <MemoryRouter initialEntries={['/login']}>
          <SnackbarProvider maxSnack={6} autoHideDuration={6000}>
            <Routes>
              <Route path="/login" element={<Login />} />
            </Routes>
          </SnackbarProvider>
        </MemoryRouter>
      </Provider>
    );

  it('handles correct login', async () => {
    const state = { token: initialState };
    const store = mockStore(state);
    component({ store: store });
    const arg = { username: 'jst', password: 'yop' };
    await act(async () => {
      await store.dispatch(getTokenAsync(arg));
    });
    const want = [
      {
        type: 'login/fetchToken/pending',
        payload: undefined,
        meta: {
          arg: arg,
          requestStatus: 'pending',
        },
      },
      {
        type: 'login/fetchToken/fulfilled',
        payload: {
          access_token: 'dummy_new_access_token',
          refresh_token: 'dummy_new_refresh_token',
          expires_in: 3600,
        },
        meta: {
          arg: arg,
          requestStatus: 'fulfilled',
        },
      },
    ];
    expect(store.getActions()).toMatchObject(want);
    expect(store.getActions()[0].meta.requestId).toEqual(
      store.getActions()[1].meta.requestId
    );
  });
  it('handles failed login', async () => {
    const state = { token: initialState };
    const store = mockStore(state);
    component({ store });
    const arg = {
      username: 'dummy_invalid_login',
      password: 'dummy_invalid_password',
    };
    await act(async () => {
      await store.dispatch(getTokenAsync(arg));
    });
    const want = [
      {
        type: 'login/fetchToken/pending',
        payload: undefined,
        meta: {
          arg: arg,
          requestId: expect.stringMatching(/.*/),
          requestStatus: 'pending',
        },
      },
      {
        type: 'login/fetchToken/rejected',
        payload: undefined,
        error: {
          message: 'Login failed.',
        },
        meta: {
          aborted: false,
          arg: arg,
          condition: false,
          rejectedWithValue: false,
          requestId: expect.stringMatching(/.*/),
          requestStatus: 'rejected',
        },
      },
    ];
    expect(store.getActions()).toMatchObject(want);
    expect(store.getActions()[0].meta.requestId).toEqual(
      store.getActions()[1].meta.requestId
    );
  });
  it('handles token retrieval from refresh_token', async () => {
    const state = {
      token: { ...initialState, refresh_token: 'dummy_refresh_token' },
    };
    const store = mockStore(state);
    component({ store: store });
    await act(async () => {
      await store.dispatch(getTokenFromRefreshAsync());
    });
    const want = [
      {
        type: 'login/fetchTokenFromRefresh/pending',
        payload: undefined,
        meta: {
          requestStatus: 'pending',
        },
      },
      {
        type: 'login/fetchTokenFromRefresh/fulfilled',
        payload: {
          access_token: 'dummy_new_access_token',
          refresh_token: 'dummy_new_refresh_token',
          expires_in: 3600,
        },
        meta: {
          requestStatus: 'fulfilled',
        },
      },
    ];
    expect(store.getActions()).toMatchObject(want);
    expect(store.getActions()[0].meta.requestId).toEqual(
      store.getActions()[1].meta.requestId
    );
  });
  it('renders a link to sign up', async () => {
    const state = { token: initialState };
    const store = mockStore(state);
    const { getByText } = component({ store: store });
    getByText('login.noAccountYet');
    const button = getByText('login.signUp');
    const href = button.getAttribute('href');
    expect(href).toEqual('/signup');
  });
});
