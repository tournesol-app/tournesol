import React from 'react';
import { render } from '@testing-library/react';
import { act } from 'react-dom/test-utils';
import { MemoryRouter } from 'react-router-dom';
import { Switch, Route } from 'react-router-dom';
import configureStore, {
  MockStoreCreator,
  MockStoreEnhanced,
} from 'redux-mock-store';
import { Provider } from 'react-redux';
import thunk, { ThunkDispatch } from 'redux-thunk';
import { AnyAction } from '@reduxjs/toolkit';
import fetchMock from 'fetch-mock-jest';
import Login from './Login';
import { LoginState } from './LoginState.model';
import {
  initialState,
  getTokenAsync,
  getTokenFromRefreshAsync,
} from './loginSlice';

export interface MockState {
  token: LoginState;
}

export const mockStore: MockStoreCreator<
  MockState,
  ThunkDispatch<LoginState, undefined, AnyAction>
> = configureStore([thunk]);

const api_url = process.env.REACT_APP_API_URL;
const client_id = process.env.REACT_APP_OAUTH_CLIENT_ID || '';
const client_secret = process.env.REACT_APP_OAUTH_CLIENT_SECRET || '';
fetchMock
  .mock(
    {
      name: 'valid_login',
      url: api_url + '/o/token/',
      method: 'POST',
      headers: {
        Authorization: 'Basic ' + btoa(client_id + ':' + client_secret),
      },
      functionMatcher: (_, { body }) => {
        const params = new URLSearchParams(body?.toString());
        return (
          params.get('grant_type') === 'password' &&
          params.get('username') === 'jst' &&
          params.get('password') === 'yop' &&
          params.get('scope') === 'read write groups'
        );
      },
    },
    {
      status: 200,
      body: {
        access_token: 'dummy_new_access_token',
        refresh_token: 'dummy_new_refresh_token',
        expires_in: 3600,
      },
    },
    { sendAsJson: true }
  )
  .mock(
    {
      name: 'invalid_login',
      url: api_url + '/o/token/',
      method: 'POST',
      functionMatcher: (_, { headers, body }) => {
        const params = new URLSearchParams(body?.toString());
        if (!headers) {
          return false;
        }
        return (
          params.get('grant_type') === 'password' &&
          // TODO figure this out
          ((headers as any).Authorization !==
            'Basic ' + btoa(client_id + ':' + client_secret) ||
            params.get('username') !== 'jst' ||
            params.get('password') !== 'yop' ||
            params.get('scope') !== 'read write groups')
        );
      },
    },
    {
      status: 401,
      body: {},
    },
    { sendAsJson: true }
  )
  .mock(
    {
      name: 'token_from_refresh_token',
      url: api_url + '/o/token/',
      method: 'POST',
      headers: {
        Authorization: 'Basic ' + btoa(client_id + ':' + client_secret),
      },
      functionMatcher: (_, { body }) => {
        const params = new URLSearchParams(body?.toString());
        return (
          params.get('grant_type') === 'refresh_token' &&
          params.get('refresh_token') === 'dummy_refresh_token' &&
          params.get('scope') === 'read write groups'
        );
      },
    },
    {
      status: 200,
      body: {
        access_token: 'dummy_new_access_token',
        refresh_token: 'dummy_new_refresh_token',
        expires_in: 3600,
      },
    },
    { sendAsJson: true }
  );

describe('login feature', () => {
  const component = ({ store }: { store: MockStoreEnhanced<MockState> }) =>
    render(
      <Provider store={store}>
        <MemoryRouter initialEntries={['/login']}>
          <Switch>
            <Route path="/login">
              <Login />
            </Route>
          </Switch>
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
          requestId: expect.stringMatching(/.*/),
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
          requestId: expect.stringMatching(/.*/),
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
    const state = { token: initialState };
    const store = mockStore(state);
    component({ store: store });
    await act(async () => {
      await store.dispatch(getTokenFromRefreshAsync('dummy_refresh_token'));
    });
    const want = [
      {
        type: 'login/fetchTokenFromRefresh/pending',
        payload: undefined,
        meta: {
          arg: 'dummy_refresh_token',
          requestId: expect.stringMatching(/.*/),
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
          arg: 'dummy_refresh_token',
          requestId: expect.stringMatching(/.*/),
          requestStatus: 'fulfilled',
        },
      },
    ];
    expect(store.getActions()).toMatchObject(want);
    expect(store.getActions()[0].meta.requestId).toEqual(
      store.getActions()[1].meta.requestId
    );
  });
});
