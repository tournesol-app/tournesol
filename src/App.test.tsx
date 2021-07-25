import React from 'react';
import { render } from '@testing-library/react';
import { Provider } from 'react-redux';
import { createStore, combineReducers } from 'redux';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import drawerOpenReducer from './features/frame/drawerOpenSlice';
import { ThemeProvider } from '@material-ui/styles';
import { theme } from './theme';

const renderComponent = (drawerOpen: boolean) =>
  render(
    <Provider
      store={createStore(combineReducers({ drawerOpen: drawerOpenReducer }), {
        drawerOpen: { value: drawerOpen },
      })}
    >
      <ThemeProvider theme={theme}>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </ThemeProvider>
    </Provider>
  );

test('renders Tournesol banner', () => {
  const { getByText } = renderComponent(true);
  expect(getByText(/Tournesol/i)).toBeInTheDocument();
});
