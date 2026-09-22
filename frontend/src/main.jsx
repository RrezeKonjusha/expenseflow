import React from 'react';
import ReactDOM from 'react-dom/client';
import { Provider } from 'react-redux';
import { RouterProvider } from 'react-router-dom';
import { CssBaseline, ThemeProvider } from '@mui/material';
import { SnackbarProvider } from 'notistack';
import { store } from './app/store';
import { router } from './app/router';
import { theme } from './app/theme';
import { injectStore } from './api/client';
import AuthBootstrap from './features/auth/AuthBootstrap';

injectStore(store);

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <Provider store={store}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <SnackbarProvider
          maxSnack={3}
          autoHideDuration={3500}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        >
          <AuthBootstrap>
            <RouterProvider router={router} />
          </AuthBootstrap>
        </SnackbarProvider>
      </ThemeProvider>
    </Provider>
  </React.StrictMode>,
);
