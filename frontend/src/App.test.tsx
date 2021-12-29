import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import { render } from '@testing-library/react';
import { ThemeProvider, Theme, StyledEngineProvider } from '@mui/material/styles';
import { Provider } from 'react-redux';
import { createStore, combineReducers } from 'redux';

import App from './App';
import drawerOpenReducer from './features/frame/drawerOpenSlice';
import loginReducer, { initialState } from 'src/features/login/loginSlice';
import { theme } from './theme';


declare module '@mui/styles/defaultTheme' {
  // eslint-disable-next-line @typescript-eslint/no-empty-interface
  interface DefaultTheme extends Theme {}
}


const renderComponent = (drawerOpen: boolean) =>
  render(
    <Provider
      store={createStore(
        combineReducers({
          drawerOpen: drawerOpenReducer,
          token: loginReducer,
        }),
        {
          drawerOpen: { value: drawerOpen },
          token: initialState,
        }
      )}
    >
      <StyledEngineProvider injectFirst>
        <ThemeProvider theme={theme}>
          <BrowserRouter>
            <App />
          </BrowserRouter>
        </ThemeProvider>
      </StyledEngineProvider>
    </Provider>
  );

test('Home page renders and contains the word "Tournesol"', () => {
  const { getAllByText } = renderComponent(true);
  expect(getAllByText(/Tournesol/i).length).toBeGreaterThan(0);
});
