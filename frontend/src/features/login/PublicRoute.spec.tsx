import React from 'react';
import { MemoryRouter, Switch } from 'react-router-dom';
import { render } from '@testing-library/react';
import { waitFor } from '@testing-library/dom';
import { Provider } from 'react-redux';
import { MockStoreEnhanced } from 'redux-mock-store';

import { initialState } from './loginSlice';
import PublicRoute from './PublicRoute';
import { mockStore, MockState } from './Login.spec.tsx';

describe('Public Route component', () => {
  const renderComponent = (store: MockStoreEnhanced<MockState>) =>
    render(
      <Provider store={store}>
        <MemoryRouter initialEntries={['/']}>
          <Switch>
            <PublicRoute path="/">Public Page</PublicRoute>
          </Switch>
        </MemoryRouter>
      </Provider>
    );

  it('should render the page when not logged in', async () => {
    const { getByText } = renderComponent(
      mockStore({
        token: initialState,
      })
    );
    await waitFor(() => getByText('Public Page'));
  });

  it('should render the page when logged in', async () => {
    const anHourLater = new Date(new Date().getTime() + 3600000);

    const store = mockStore({
      token: {
        ...initialState,
        access_token: 'dummy_token',
        access_token_expiration_date: anHourLater.toString(),
      },
    });
    const { getByText } = renderComponent(store);
    await waitFor(() => getByText('Public Page'));
  });

  it('should refresh the login token when possible', async () => {
    const store = mockStore({
      token: { ...initialState, refresh_token: 'dummy_refresh_token' },
    });

    const component = renderComponent(store);
    const { getByText } = component;

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

    await waitFor(() => getByText('Public Page'));
    await waitFor(() => expect(store.getActions()).toMatchObject(want));
  });
});
