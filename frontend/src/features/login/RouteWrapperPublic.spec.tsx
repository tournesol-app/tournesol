import React from 'react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { render, screen } from '@testing-library/react';
import { waitFor } from '@testing-library/dom';
import { Provider } from 'react-redux';
import { MockStoreEnhanced } from 'redux-mock-store';

import { initialState } from './loginSlice';
import { mockStore, MockState } from './Login.spec';
import RouteWrapper from './RouteWrapper';

describe('RouteWrapper - public route', () => {
  const renderComponent = (store: MockStoreEnhanced<MockState>) =>
    render(
      <Provider store={store}>
        <MemoryRouter initialEntries={['/public']}>
          <Routes>
            <Route
              path="/public"
              element={<RouteWrapper>Public page</RouteWrapper>}
            />
          </Routes>
        </MemoryRouter>
      </Provider>
    );

  it('should render the page for anonymous users', async () => {
    renderComponent(
      mockStore({
        token: initialState,
      })
    );

    expect(screen.getByText('Public page')).toBeVisible();
  });

  const anHourLater = new Date(new Date().getTime() + 3600000);
  const tenMinutesLater = new Date(new Date().getTime() + 600000);

  it('should render the page for authenticated users', async () => {
    const store = mockStore({
      token: {
        ...initialState,
        access_token: 'dummy_token',
        access_token_expiration_date: anHourLater.toString(),
      },
    });
    renderComponent(store);
    expect(screen.getByText('Public page')).toBeVisible();
  });

  const token_refresh_expected_actions = [
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

  it('should refresh the login token when needed', async () => {
    const store = mockStore({
      token: { ...initialState, refresh_token: 'dummy_refresh_token' },
    });
    const { getByText } = renderComponent(store);
    expect(screen.getByText('Public page')).toBeVisible();
    await waitFor(() =>
      expect(store.getActions()).toMatchObject(token_refresh_expected_actions)
    );
  });

  it('should not refresh the login token if logged in', async () => {
    const store = mockStore({
      token: {
        ...initialState,
        refresh_token: 'dummy_refresh_token',
        access_token: 'dummy_token',
        access_token_expiration_date: anHourLater.toString(),
      },
    });
    renderComponent(store);
    expect(screen.getByText('Public page')).toBeVisible();
    await waitFor(() => expect(store.getActions()).toMatchObject([]));
  });

  it('should refresh the login if it expires in 10 minutes', async () => {
    const store = mockStore({
      token: {
        ...initialState,
        refresh_token: 'dummy_refresh_token',
        access_token: 'dummy_token',
        access_token_expiration_date: tenMinutesLater.toString(),
      },
    });
    renderComponent(store);
    expect(screen.getByText('Public page')).toBeVisible();
    await waitFor(() =>
      expect(store.getActions()).toMatchObject(token_refresh_expected_actions)
    );
  });
});
