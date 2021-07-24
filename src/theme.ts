import { createTheme } from '@material-ui/core/styles';

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
