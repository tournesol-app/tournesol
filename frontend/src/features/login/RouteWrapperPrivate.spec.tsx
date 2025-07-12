import React from 'react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { render, screen } from '@testing-library/react';
import { Provider } from 'react-redux';
import { combineReducers, createStore } from 'redux';

import loginReducer, { initialState } from './loginSlice';
import { LoginState } from './LoginState.model';
import RouteWrapper from './RouteWrapper';

const renderComponent = ({
  login,
  targetPath,
  loginPage,
  protectedPage,
}: {
  login: LoginState;
  targetPath: string;
  loginPage: string;
  protectedPage: string;
}) =>
  render(
    <Provider
      store={createStore(combineReducers({ token: loginReducer }), {
        token: login,
      })}
    >
      <MemoryRouter initialEntries={[targetPath]}>
        <Routes>
          <Route
            path="/login"
            element={<RouteWrapper>{loginPage}</RouteWrapper>}
          />
          <Route
            path={targetPath}
            element={<RouteWrapper auth={true}>{protectedPage}</RouteWrapper>}
          />
        </Routes>
      </MemoryRouter>
    </Provider>
  );

describe('RouteWrapper - private route', () => {
  it('should render protected page for authenticated users', async () => {
    const anHourInMS = 1000 * 60 * 60;
    const now = new Date();
    const anHourLater = new Date(now.getTime() + anHourInMS);
    const login = { ...initialState };
    login.access_token = 'dummy_token';
    login.access_token_expiration_date = anHourLater.toString();

    renderComponent({
      login: login,
      targetPath: '/protected',
      loginPage: 'login_marker',
      protectedPage: 'protected_marker',
    });

    screen.getByText('protected_marker');
  });

  it('should render login page for anonymous users', async () => {
    renderComponent({
      login: initialState,
      targetPath: '/protected',
      loginPage: 'login_marker',
      protectedPage: 'protected_marker',
    });

    screen.getByText('login_marker');
  });
});
