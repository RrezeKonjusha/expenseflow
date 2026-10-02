import { Box } from '@mui/material';
import { StatCard } from './common';

export default {
  title: 'Components/StatCard',
  component: StatCard,
  decorators: [(Story) => <Box sx={{ width: 276 }}>{Story()}</Box>],
};

export const Default = { args: { label: 'Drafts', value: 3 } };

export const WithHint = { args: { label: 'Waiting for approval', value: 2, hint: '€380.00' } };

/** Before the dashboard data arrives the value is a skeleton. */
export const Loading = {
  args: { label: 'Spent this month', value: undefined, hint: 'approved + reimbursed' },
};
