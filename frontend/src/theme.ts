import { createTheme, responsiveFontSizes, adaptV4Theme } from '@mui/material/styles';

export const theme = responsiveFontSizes(
  createTheme(adaptV4Theme({
    palette: {
      primary: {
        main: '#ffc800',
      },
      secondary: {
        main: '#506AD4',
      },
      text: {
        primary: '#1d1a14',
        secondary: '#4a473e',
      },
    },
    typography: {
      h1: {
        fontSize: '2.4rem',
      },
      h2: {
        fontSize: '2.1rem',
      },
      h3: {
        fontSize: '1.8rem',
        fontWeight: 600,
      },
      h4: {
        fontSize: '1.5rem',
        fontWeight: 600,
      },
      fontFamily: [
        'Poppins',
        '-apple-system',
        'BlinkMacSystemFont',
        '"Segoe UI"',
        'Roboto',
        '"Helvetica Neue"',
        'Arial',
        'sans-serif',
        '"Apple Color Emoji"',
        '"Segoe UI Emoji"',
        '"Segoe UI Symbol"',
      ].join(','),
    },
    overrides: {
      MuiDrawer: {
        docked: {
          width: 240,
        },
      },
    },
  }))
);
