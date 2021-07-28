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
import Cookies from 'js-cookie';
import Login from './Login';
import { LoginState } from './LoginState.model';
import {
  initialState,
  getTokenAsync,
  getLoginAsync,
  getUserInfoAsync,
  getTokenFromRefreshAsync,
} from './loginSlice';
import { fetchAuthorization } from './loginAPI';

interface MockState {
  token: LoginState;
}

describe('login feature', () => {
  const mockStore: MockStoreCreator<
    MockState,
    ThunkDispatch<LoginState, undefined, AnyAction>
  > = configureStore([thunk]);
  const api_url = process.env.REACT_APP_API_URL;
  const client_id = process.env.REACT_APP_OAUTH_CLIENT_ID || '';
  const client_secret = process.env.REACT_APP_OAUTH_CLIENT_SECRET || '';
  fetchMock
    .mock(
      {
        url: api_url + '/admin/login/',
        method: 'GET',
      },
      () => {
        Cookies.set('csrftoken', 'dummy_csrf', { expires: 1, path: '' });
        return {
          status: 200,
        };
      }
    )
    .mock(
      {
        name: 'valid_login',
        url: api_url + '/admin/login/',
        method: 'POST',
        functionMatcher: (_, { body }) => {
          const params = new URLSearchParams(body?.toString());
          return (
            params.get('username') === 'jst' &&
            params.get('password') === 'yop' &&
            params.get('csrfmiddlewaretoken') === 'dummy_csrf'
          );
        },
      },
      {
        status: 302,
        redirectUrl: api_url + '/admin/',
      }
    )
    .mock(
      {
        name: 'invalid_login',
        url: api_url + '/admin/login/',
        method: 'POST',
        functionMatcher: (_, { body }) => {
          const params = new URLSearchParams(body?.toString());
          return (
            params.get('username') !== 'jst' ||
            params.get('password') !== 'yop' ||
            params.get('csrfmiddlewaretoken') !== 'dummy_csrf'
          );
        },
      },
      {
        status: 302,
        redirectUrl: api_url + '/admin/login/',
      }
    )
    .mock(
      {
        url: api_url + '/o/authorize/',
        method: 'GET',
        query: {
          response_type: 'code',
          client_id: client_id,
          redirect_uri: api_url + '/admin/',
        },
      },
      (url: any) => {
        const reqParams = new URLSearchParams(url);
        const state = reqParams.get('state');
        const params = new URLSearchParams();
        params.set('code', 'dummy_code');
        params.set('state', state ?? '');
        return {
          status: 302,
          redirectUrl: api_url + '/admin/login/?' + params.toString(),
        };
      }
    )
    .mock(
      {
        name: 'token_from_code',
        url: api_url + '/o/token/',
        method: 'POST',
        functionMatcher: (_, { body }) => {
          const params = new URLSearchParams(body?.toString());
          return (
            params.get('code') === 'dummy_code' &&
            params.get('redirect_uri') === api_url + '/admin/' &&
            params.get('grant_type') === 'authorization_code' &&
            params.get('client_id') === client_id &&
            params.get('client_secret') == client_secret &&
            params.get('scope') === 'read write groups'
          );
        },
      },
      {
        status: 200,
        body: {
          access_token: 'dummy_access_token',
          refresh_token: 'dummy_refresh_token',
          id_token: 'dummy_id_token',
          expires_in: 3600,
        },
      },
      { sendAsJson: true }
    )
    .mock(
      {
        name: 'token_from_refresh_token',
        url: api_url + '/o/token/',
        method: 'POST',
        functionMatcher: (_, { body }) => {
          const params = new URLSearchParams(body?.toString());
          return (
            params.get('refresh_token') === 'dummy_refresh_token' &&
            params.get('redirect_uri') === api_url + '/admin/' &&
            params.get('grant_type') === 'refresh_token' &&
            params.get('client_id') === client_id &&
            params.get('client_secret') == client_secret &&
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
        url: api_url + '/o/userinfo/',
        method: 'GET',
        headers: {
          Authorization: 'Bearer dummy_access_token',
        },
      },
      {
        status: 200,
        body: {
          sub: 'dummy_sub',
          username: 'dummy_username',
          preferred_username: 'dummy_preferred_username',
          email: 'dummy_email',
          first_name: 'dummy_first_name',
          last_name: 'dummy_last_name',
        },
      }
    );

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
      await store.dispatch(getLoginAsync(arg));
    });
    const want = [
      {
        type: 'login/fetchLogin/pending',
        payload: undefined,
        meta: {
          arg: arg,
          requestId: expect.stringMatching(/.*/),
          requestStatus: 'pending',
        },
      },
      {
        type: 'login/fetchLogin/fulfilled',
        payload: undefined,
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
      await store.dispatch(getLoginAsync(arg));
    });
    const want = [
      {
        type: 'login/fetchLogin/pending',
        payload: undefined,
        meta: {
          arg: arg,
          requestId: expect.stringMatching(/.*/),
          requestStatus: 'pending',
        },
      },
      {
        type: 'login/fetchLogin/rejected',
        payload: undefined,
        error: {
          message: 'login failed',
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
  it('handles successful authorization', async () => {
    let resp: { data: string } = { data: '' };
    await act(async () => {
      resp = await fetchAuthorization();
    });
    expect(resp.data).toEqual('dummy_code');
  });
  it('handles token retrieval from code', async () => {
    const state = { token: initialState };
    const store = mockStore(state);
    component({ store: store });
    await act(async () => {
      await store.dispatch(getTokenAsync('dummy_code'));
    });
    const want = [
      {
        type: 'login/fetchToken/pending',
        payload: undefined,
        meta: {
          arg: 'dummy_code',
          requestId: expect.stringMatching(/.*/),
          requestStatus: 'pending',
        },
      },
      {
        type: 'login/fetchToken/fulfilled',
        payload: {
          access_token: 'dummy_access_token',
          refresh_token: 'dummy_refresh_token',
          id_token: 'dummy_id_token',
          expires_in: 3600,
        },
        meta: {
          arg: 'dummy_code',
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
  it('handles userinfo retrieval', async () => {
    const state = { token: initialState };
    const store = mockStore(state);
    component({ store: store });
    await act(async () => {
      await store.dispatch(getUserInfoAsync('dummy_access_token'));
    });
    const want = [
      {
        type: 'login/fetchUserInfo/pending',
        payload: undefined,
        meta: {
          arg: 'dummy_access_token',
          requestId: expect.stringMatching(/.*/),
          requestStatus: 'pending',
        },
      },
      {
        type: 'login/fetchUserInfo/fulfilled',
        payload: {
          sub: 'dummy_sub',
          username: 'dummy_username',
          preferred_username: 'dummy_preferred_username',
          email: 'dummy_email',
          first_name: 'dummy_first_name',
          last_name: 'dummy_last_name',
        },
        meta: {
          arg: 'dummy_access_token',
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
