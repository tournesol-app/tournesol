import React from 'react';
import { render } from '@testing-library/react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import loginReducer, { initialState } from './loginSlice';
import { LoginState } from './LoginState.model';
import Login from './Login';
import { MemoryRouter } from 'react-router-dom';
import { Switch, Route } from 'react-router-dom';
import { FetchMock } from '@react-mock/fetch';
import { fireEvent, waitFor } from '@testing-library/dom';
import { act } from 'react-dom/test-utils';

describe('login feature', () => {
  const api_url = process.env.REACT_APP_API_URL;

  const component = ({
    login,
    fetchMocks,
  }: {
    login: LoginState;
    fetchMocks: any;
  }) =>
    render(
      <Provider store={configureStore({ reducer: { token: loginReducer } })}>
        <MemoryRouter initialEntries={['/login']}>
          <Switch>
            <Route path="/login">
              {/* <FetchMock mocks={fetchMocks}> */}
              <Login />
              {/* </FetchMock> */}
            </Route>
          </Switch>
        </MemoryRouter>
      </Provider>
    );

  it('should set CSRF token on login', async () => {
    const fetchMocks = [
      {
        matcher: api_url + '/admin/login/',
        method: 'GET',
        response: () => {
          const cookieString =
            'csrftoken=dummy_csrf; Max-Age=3600; Path=/admin/login/;';
          document.cookie = cookieString;
          return {
            status: 200,
            config: {
              headers: {
                'Set-Cookie': cookieString,
              },
            },
          };
        },
      },
      {
        matcher: api_url + '/admin/login/',
        method: 'POST',
        response: () => {
          return {
            status: 200,
            config: {
              redirectUrl: '/admin/',
            },
          };
        },
      },
    ];
    let rendered = component({ login: initialState, fetchMocks: fetchMocks });
    act(() => {
      fireEvent.click(rendered.getByRole('login-button'));
    });
    await waitFor(() => rendered.getAllByText(/User/i));
  });
});
