import { createTheme } from '@mui/material/styles';

export const theme = createTheme({
  palette: { primary: { main: '#1565c0' }, background: { default: '#f6f7fb' } },
  shape: { borderRadius: 10 },
  typography: { fontFamily: 'Inter, Roboto, system-ui, sans-serif', h5: { fontWeight: 600 } },
  components: {
    MuiButton: {
      defaultProps: { disableElevation: true },
      styleOverrides: { root: { textTransform: 'none' } },
    },
    MuiPaper: { defaultProps: { elevation: 0 }, styleOverrides: { root: { border: '1px solid #e3e6ee' } } },
    MuiAppBar: { styleOverrides: { root: { border: 'none' } } },
  },
});
