import { Stack } from '@mui/material';
import { STATUSES, StatusChip } from './common';

export default {
  title: 'Components/StatusChip',
  component: StatusChip,
  argTypes: {
    status: { control: 'select', options: STATUSES },
    size: { control: 'radio', options: ['small', 'medium'] },
  },
};

export const Draft = { args: { status: 'DRAFT' } };
export const Submitted = { args: { status: 'SUBMITTED' } };
export const Approved = { args: { status: 'APPROVED' } };
export const Rejected = { args: { status: 'REJECTED' } };
export const Reimbursed = { args: { status: 'REIMBURSED' } };

/** Every status side by side, as in the expense list. */
export const AllStatuses = {
  render: () => (
    <Stack direction="row" spacing={1}>
      {STATUSES.map((s) => (
        <StatusChip key={s} status={s} />
      ))}
    </Stack>
  ),
};
