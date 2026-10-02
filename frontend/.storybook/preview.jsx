import { CssBaseline, ThemeProvider } from '@mui/material';
import { theme } from '../src/app/theme';

// Same MUI theme as the app, so stories look exactly like the pages.
const preview = {
  decorators: [
    (Story) => (
      <ThemeProvider theme={theme}>
        <CssBaseline />
        {Story()}
      </ThemeProvider>
    ),
  ],
  parameters: { layout: 'padded' },
};
export default preview;
