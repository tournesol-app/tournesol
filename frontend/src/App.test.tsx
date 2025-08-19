import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import { Provider } from 'react-redux';
import { AnyAction } from '@reduxjs/toolkit';
import configureStore, {
  MockStoreCreator,
  MockStoreEnhanced,
} from 'redux-mock-store';
import thunk, { ThunkDispatch } from 'redux-thunk';
import { render, screen } from '@testing-library/react';
import { waitFor } from '@testing-library/dom';

import { ThemeProvider, StyledEngineProvider } from '@mui/material/styles';

import { LoginState } from 'src/features/login/LoginState.model';
import { initialState } from 'src/features/login/loginSlice';
import App from './App';
import { theme } from './theme';
import { RootState } from './app/store';
import { mockAppRequests } from './mockUtils';

type MockState = Partial<RootState>;

const mockStore: MockStoreCreator<
  MockState,
  ThunkDispatch<LoginState, undefined, AnyAction>
> = configureStore([thunk]);

const renderComponent = (mockedStore?: MockStoreEnhanced<MockState>) => {
  const store =
    mockedStore ??
    mockStore({
      drawerOpen: { value: true },
      token: initialState,
      settings: { settings: {} },
    });

  return render(
    <Provider store={store}>
      <StyledEngineProvider injectFirst>
        <ThemeProvider theme={theme}>
          <BrowserRouter>
            <App />
          </BrowserRouter>
        </ThemeProvider>
      </StyledEngineProvider>
    </Provider>
  );
};

test('Home page renders and contains the word "Tournesol"', () => {
  mockAppRequests();
  const { getAllByText } = renderComponent();
  expect(getAllByText(/Tournesol/i).length).toBeGreaterThan(0);
});

describe('token management in App', () => {
  const anHourLater = new Date(new Date().getTime() + 3600000);
  const tenMinutesLater = new Date(new Date().getTime() + 600000);
  const token_refresh_expected_fulfilled_action = {
    type: 'login/fetchTokenFromRefresh/fulfilled',
    payload: {
      access_token: 'dummy_new_access_token',
      refresh_token: 'dummy_new_refresh_token',
      expires_in: 3600,
    },
    meta: {
      requestId: expect.stringMatching(/.*/),
      requestStatus: 'fulfilled',
    },
  };

  beforeAll(() => {
    mockAppRequests();
  });

  it('should not refresh the login token if logged in', async () => {
    const store = mockStore({
      settings: { settings: {} },
      drawerOpen: { value: false },
      token: {
        ...initialState,
        refresh_token: 'dummy_refresh_token_2',
        access_token: 'dummy_token',
        access_token_expiration_date: anHourLater.toString(),
      },
    });
    renderComponent(store);
    expect(screen.getByText('menu.home')).toBeVisible();
    await waitFor(() =>
      expect(
        store.getActions().filter(({ type }) => type.startsWith('login/'))
      ).toMatchObject([])
    );
  });

  it('should refresh the login if it expires in less than 10 minutes', async () => {
    const store = mockStore({
      settings: { settings: {} },
      drawerOpen: { value: false },
      token: {
        ...initialState,
        refresh_token: 'dummy_refresh_token_3',
        access_token: 'dummy_token',
        access_token_expiration_date: tenMinutesLater.toString(),
      },
    });
    renderComponent(store);
    expect(screen.getByText('menu.home')).toBeVisible();
    await waitFor(() =>
      expect(store.getActions()).toContainEqual(
        token_refresh_expected_fulfilled_action
      )
    );
  });
});
