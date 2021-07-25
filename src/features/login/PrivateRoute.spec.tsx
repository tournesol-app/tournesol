import React from 'react';
import { render } from '@testing-library/react';
import { waitFor } from '@testing-library/dom';
import { Provider } from 'react-redux';
import { combineReducers, createStore } from 'redux';
import loginReducer, { initialState } from './loginSlice';
import { LoginState } from './LoginState.model';
import { PrivateRoute } from './PrivateRoute';
import { MemoryRouter } from 'react-router-dom';
import { Switch, Route } from 'react-router-dom';

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
        <Switch>
          <Route path="/login">{loginPage}</Route>
          <PrivateRoute path={targetPath}>{protectedPage}</PrivateRoute>
        </Switch>
      </MemoryRouter>
    </Provider>
  );

test('renders protected page when logged', async () => {
  const anHourInMS = 1000 * 60 * 60;
  const now = new Date();
  const anHourLater = new Date(now.getTime() + anHourInMS);
  let login = { ...initialState };
  login.access_token = 'dummy_token';
  login.access_token_expiration_date = anHourLater.toString();

  const { getByText } = renderComponent({
    login: login,
    targetPath: '/protected',
    loginPage: 'login_marker',
    protectedPage: 'protected_marker',
  });
  await waitFor(() => getByText('protected_marker'));
});

test('renders login page when not logged', async () => {
  const { getByText } = renderComponent({
    login: initialState,
    targetPath: '/protected',
    loginPage: 'login_marker',
    protectedPage: 'protected_marker',
  });
  await waitFor(() => getByText('login_marker'));
});
