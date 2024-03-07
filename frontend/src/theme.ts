import { createTheme } from '@mui/material/styles';

declare module '@mui/material/styles' {
  interface Palette {
    neutral: Palette['primary'];
  }

  interface PaletteOptions {
    neutral: PaletteOptions['primary'];
  }

  interface TypeBackground {
    primary: string;
    menu: string;
    emphatic?: string;
  }

  interface ZIndex {
    videoCardDuration: number;
  }
}

export const theme = createTheme({
  palette: {
    primary: {
      main: '#ffc800',
    },
    secondary: {
      main: '#506AD4',
    },
    neutral: {
      light: '#C6BFA5',
      main: '#A09B87',
      dark: '#806300',
    },
    text: {
      primary: '#1d1a14',
      secondary: '#4a473e',
    },
    background: {
      primary: '#FAFAFA',
      menu: '#FAF8F3',
      emphatic: '#1282B2',
    },
  },
  typography: {
    h1: {
      fontSize: '1.75rem',
    },
    h2: {
      fontSize: '1.6rem',
    },
    h3: {
      fontSize: '1.4rem',
      fontWeight: 600,
    },
    h4: {
      fontSize: '1.25rem',
      fontWeight: 600,
    },
    h5: {
      fontSize: '1.08rem',
      fontWeight: 600,
    },
    h6: {
      fontSize: '1rem',
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
  zIndex: {
    videoCardDuration: 1,
  },
  components: {
    MuiInputBase: {
      styleOverrides: {
        input: {
          // Make sure that inputs have font-size "16px" by default
          // instead of "1rem" which may be equal to a smaller value on small screens.
          // Safari on iOS would automatically zoom when focusing a input with
          // font-size < 16px, not desirable in most cases (e.g in EntitySearchInput).
          fontSize: '16px',
        },
      },
    },
  },
});
