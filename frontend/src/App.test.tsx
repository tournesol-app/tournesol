import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import { Provider } from 'react-redux';
import { AnyAction } from '@reduxjs/toolkit';
import configureStore, { MockStoreCreator } from 'redux-mock-store';
import thunk, { ThunkDispatch } from 'redux-thunk';
import { render } from '@testing-library/react';

import { ThemeProvider, StyledEngineProvider } from '@mui/material/styles';

import { LoginState } from 'src/features/login/LoginState.model';
import { initialState } from 'src/features/login/loginSlice';
import App from './App';
import { theme } from './theme';

export interface MockState {
  token: LoginState;
  drawerOpen: { value: boolean };
}

export const mockStore: MockStoreCreator<
  MockState,
  ThunkDispatch<LoginState, undefined, AnyAction>
> = configureStore([thunk]);

const renderComponent = (drawerOpen: boolean) => {
  const store = mockStore({
    token: initialState,
    drawerOpen: { value: drawerOpen },
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
  const { getAllByText } = renderComponent(true);
  expect(getAllByText(/Tournesol/i).length).toBeGreaterThan(0);
});
