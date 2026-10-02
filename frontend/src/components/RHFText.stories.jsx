import { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { Box } from '@mui/material';
import { RHFText } from './FormFields';

// RHFText needs a react-hook-form control; this wrapper provides one and can preset an error.
function Field({ error, defaultValue = '', ...props }) {
  const { control, setError } = useForm({ defaultValues: { [props.name]: defaultValue } });
  useEffect(() => {
    if (error) setError(props.name, { type: 'server', message: error });
  }, [error, props.name, setError]);
  return (
    <Box sx={{ width: 360 }}>
      <RHFText control={control} {...props} />
    </Box>
  );
}

export default { title: 'Components/RHFText', component: Field };

export const Default = { args: { name: 'description', label: 'Description' } };

export const WithHelperText = {
  args: {
    name: 'attendees',
    label: 'Attendees',
    type: 'number',
    defaultValue: 2,
    helperText: 'Max 25 EUR per attendee',
  },
};

/** A server-side policy error mapped onto the field. */
export const Error = {
  args: {
    name: 'amount',
    label: 'Amount (EUR)',
    defaultValue: '60.00',
    error: 'Meals are capped at 25.00 EUR per attendee: max 25.00 EUR.',
  },
};

export const Select = {
  args: {
    name: 'type',
    label: 'Type',
    select: true,
    defaultValue: 'MEAL',
    options: [
      { value: 'MEAL', label: 'Meal' },
      { value: 'TRAVEL', label: 'Travel' },
      { value: 'EQUIPMENT', label: 'Equipment' },
    ],
  },
};
