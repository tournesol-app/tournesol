import React from 'react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { render, screen } from '@testing-library/react';
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
});
