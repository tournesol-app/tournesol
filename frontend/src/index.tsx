import React, { Suspense } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { Provider } from 'react-redux';
import { PersistGate } from 'redux-persist/integration/react';

import { SnackbarProvider } from 'notistack';

import CssBaseline from '@mui/material/CssBaseline';
import {
  ThemeProvider,
  Theme,
  StyledEngineProvider,
} from '@mui/material/styles';

import './index.css';
import './i18n';
import App from './App';
import { store, persistor } from './app/store';
import { theme } from './theme';

declare module '@mui/styles/defaultTheme' {
  // eslint-disable-next-line @typescript-eslint/no-empty-interface
  interface DefaultTheme extends Theme {}
}

const root = createRoot(document.getElementById('root') as HTMLElement);
root.render(
  <React.StrictMode>
    <Provider store={store}>
      <PersistGate loading={null} persistor={persistor}>
        <StyledEngineProvider injectFirst>
          <ThemeProvider theme={theme}>
            <CssBaseline />
            <BrowserRouter>
              <SnackbarProvider
                classes={{
                  containerAnchorOriginTopRight: 'belowTopBar',
                }}
                maxSnack={6}
                anchorOrigin={{
                  vertical: 'top',
                  horizontal: 'right',
                }}
              >
                <Suspense fallback={null}>
                  <App />
                </Suspense>
              </SnackbarProvider>
            </BrowserRouter>
          </ThemeProvider>
        </StyledEngineProvider>
      </PersistGate>
    </Provider>
  </React.StrictMode>
);
