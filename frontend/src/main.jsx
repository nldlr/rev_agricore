import { StrictMode, useContext, createContext, useState, useMemo } from 'react'
import { createRoot } from 'react-dom/client'
import {ThemeProvider, CssBaseline} from '@mui/material'
import {getTheme} from './theme.js'
import './index.css'
import App from './App.jsx'

export const ColorModeContext = createContext({ toggleColorMode: () => {} });
export const useColorMode = () => useContext(ColorModeContext);

function CustomThemeProvider({ children }) {
  const [mode, setMode] = useState('light');

  const colorMode = useMemo(
    () => ({
      toggleColorMode: () => {
        setMode((prevMode) => (prevMode === 'light' ? 'dark' : 'light'));
      },
      mode,
    }),
    [mode]
  );

  const theme = useMemo(() => getTheme(mode), [mode]);

  return (
    <ColorModeContext.Provider value={colorMode}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        {children}
      </ThemeProvider>
    </ColorModeContext.Provider>
  );
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    {/**
     * ThemeProvider is a component from Material-UI that allows you to apply the custom theme
     * to your application. Here, we are wrapping the App component with the ThemeProvider.
     */}
     <CustomThemeProvider>
      <CssBaseline />
      <App />
    </CustomThemeProvider>
  </StrictMode>,
)