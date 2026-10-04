import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#885e43',
    },
    secondary: {
      main: '#ff6f00',
    },
    text: {
      primary: '#1a1a1a', // Sets base text color for Typography
    },
  },
  typography: {
    h5: {
      color: '#1a1a1a', // Guarantees all variant="h5" elements are dark
    },
  },
  shape: {
    borderRadius: 8,
  },
});

export default theme;