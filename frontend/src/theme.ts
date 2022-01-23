import { createTheme, responsiveFontSizes } from '@mui/material/styles';

declare module '@mui/material/styles/createPalette' {
  interface Palette {
    neutral: Palette['primary'];
  }

  interface PaletteOptions {
    neutral: PaletteOptions['primary'];
  }

  interface TypeBackground {
    menu: string;
  }
}

export const theme = responsiveFontSizes(
  createTheme({
    palette: {
      primary: {
        main: '#ffc800',
      },
      secondary: {
        main: '#506AD4',
      },
      neutral: {
        main: '#A09B87',
        dark: '#806300',
      },
      text: {
        primary: '#1d1a14',
        secondary: '#4a473e',
      },
      background: {
        menu: '#FAF8F3',
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
  })
);
