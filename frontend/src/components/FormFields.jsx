import { Controller } from 'react-hook-form';
import { MenuItem, TextField } from '@mui/material';

/** TextField bound to react-hook-form, showing client and server errors. */
export function RHFText({ control, name, label, select, options = [], ...props }) {
  return (
    <Controller
      control={control}
      name={name}
      render={({ field, fieldState }) => (
        <TextField
          {...field}
          value={field.value ?? ''}
          label={label}
          select={select}
          fullWidth
          error={!!fieldState.error}
          helperText={fieldState.error?.message || props.helperText}
          inputProps={{ 'data-cy': name, ...(props.inputProps || {}) }}
          {...props}
        >
          {select &&
            options.map((o) => (
              <MenuItem key={o.value} value={o.value}>
                {o.label}
              </MenuItem>
            ))}
        </TextField>
      )}
    />
  );
}
