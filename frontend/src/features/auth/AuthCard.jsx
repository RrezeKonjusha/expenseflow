import { Box, Paper, Typography } from '@mui/material';

export default function AuthCard({ title, subtitle, children }) {
  return (
    <Box
      sx={{ minHeight: '100vh', display: 'grid', placeItems: 'center', p: 2, bgcolor: 'background.default' }}
    >
      <Paper sx={{ p: { xs: 3, sm: 4 }, width: '100%', maxWidth: 420 }}>
        <Typography variant="h6" color="primary" fontWeight={700}>
          ExpenseFlow
        </Typography>
        <Typography variant="h5" sx={{ mt: 2 }}>
          {title}
        </Typography>
        {subtitle && (
          <Typography color="text.secondary" sx={{ mb: 2 }}>
            {subtitle}
          </Typography>
        )}
        <Box sx={{ mt: 2 }}>{children}</Box>
      </Paper>
    </Box>
  );
}
