import { Box, Chip, Paper, Skeleton, Stack, Typography } from '@mui/material';
import dayjs from 'dayjs';

export const STATUS_COLORS = {
  DRAFT: 'default',
  SUBMITTED: 'info',
  APPROVED: 'success',
  REJECTED: 'error',
  REIMBURSED: 'secondary',
};

export function StatusChip({ status, size = 'small' }) {
  return <Chip size={size} label={status} color={STATUS_COLORS[status] || 'default'} variant="outlined" />;
}

export const money = (v) => Number(v ?? 0).toLocaleString('en-US', { style: 'currency', currency: 'EUR' });
export const date = (v) => (v ? dayjs(v).format('DD MMM YYYY') : '');
export const dateTime = (v) => (v ? dayjs(v).format('DD MMM YYYY, HH:mm') : '');

export function PageHeader({ title, subtitle, actions }) {
  return (
    <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} sx={{ mb: 3 }} alignItems={{ sm: 'center' }}>
      <Box sx={{ flexGrow: 1 }}>
        <Typography variant="h5">{title}</Typography>
        {subtitle && <Typography color="text.secondary">{subtitle}</Typography>}
      </Box>
      {actions && (
        <Stack direction="row" spacing={1}>
          {actions}
        </Stack>
      )}
    </Stack>
  );
}

export function StatCard({ label, value, hint }) {
  return (
    <Paper sx={{ p: 2.5, height: '100%' }}>
      <Typography variant="body2" color="text.secondary">
        {label}
      </Typography>
      <Typography variant="h5" sx={{ mt: 0.5 }}>
        {value ?? <Skeleton width={80} />}
      </Typography>
      {hint && (
        <Typography variant="caption" color="text.secondary">
          {hint}
        </Typography>
      )}
    </Paper>
  );
}

export const EXPENSE_TYPES = ['MEAL', 'TRAVEL', 'EQUIPMENT'];
export const STATUSES = ['DRAFT', 'SUBMITTED', 'APPROVED', 'REJECTED', 'REIMBURSED'];
