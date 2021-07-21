import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';
import { createTheme, ThemeProvider } from '@material-ui/core/styles';
import { BrowserRouter } from 'react-router-dom'
import { store, persistor } from './app/store';
import { Provider } from 'react-redux';
import * as serviceWorker from './serviceWorker';
import { PersistGate } from 'redux-persist/integration/react';

export const theme = createTheme({
  palette: {
    primary: {
      main: '#fdd835',
    },
    secondary: {
      main: '#336600',
    },
  },
  overrides: {
    MuiDrawer: {
      docked: {
        width: 240,
      },
    },
  },
});

ReactDOM.render(
  <React.StrictMode>
    <Provider store={store}>
      <PersistGate loading={null} persistor={persistor}>
        <ThemeProvider theme={theme}>
          <BrowserRouter>
            <App />
          </BrowserRouter>
        </ThemeProvider>
      </PersistGate>
    </Provider>
  </React.StrictMode>,
  document.getElementById('root')
);

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
serviceWorker.unregister();
reportWebVitals();
