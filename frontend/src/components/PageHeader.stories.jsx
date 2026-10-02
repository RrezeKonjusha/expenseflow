import { Button } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import { PageHeader } from './common';

export default { title: 'Components/PageHeader', component: PageHeader };

export const TitleOnly = { args: { title: 'Users' } };

export const WithSubtitle = {
  args: { title: 'Approvals', subtitle: 'Submitted expenses from your department, oldest first.' },
};

/** Page actions sit on the right and stack under the title on small screens. */
export const WithActions = {
  args: {
    title: 'Expenses',
    subtitle: 'Search, filter and open any expense you can see.',
    actions: [
      <Button key="i">Import</Button>,
      <Button key="n" variant="contained" startIcon={<AddIcon />}>
        New expense
      </Button>,
    ],
  },
};
