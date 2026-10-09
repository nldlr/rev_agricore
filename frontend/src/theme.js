import { createTheme } from '@mui/material/styles';

export const getTheme = (mode) =>
  createTheme({
    palette: {
      mode,
      primary: {
        main: '#885e43',
      },
      secondary: {
        main: '#907560',
      },
    },
    shape: {
      borderRadius: 8,
    },
  });