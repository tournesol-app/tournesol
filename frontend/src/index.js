import React from 'react';
import ReactDOM from 'react-dom';

import { createMuiTheme, ThemeProvider } from '@material-ui/core/styles';
import { BrowserRouter as Router } from 'react-router-dom';

import App from './components/App';

const theme = createMuiTheme({
  palette: {
    primary: {
      main: '#fdd835',
    },
    secondary: {
      main: '#336600',
    },
  },
});

ReactDOM.render(
  <ThemeProvider theme={theme}>
    <Router>
      <App />
    </Router>
  </ThemeProvider>,
  document.getElementById('app'),
);
