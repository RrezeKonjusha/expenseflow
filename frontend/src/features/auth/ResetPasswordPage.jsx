import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { Link as RouterLink, useParams } from 'react-router-dom';
import { Alert, Button, Stack } from '@mui/material';
import { RHFText } from '../../components/FormFields';
import { applyFieldErrors, errorMessage } from '../../api/client';
import { authApi } from '../../api/endpoints';
import AuthCard from './AuthCard';

const schema = yup.object({
  new_password: yup.string().min(10, 'At least 10 characters').required(),
  confirm: yup
    .string()
    .oneOf([yup.ref('new_password')], 'Passwords do not match')
    .required(),
});

export default function ResetPasswordPage() {
  const { uid, token } = useParams();
  const [done, setDone] = useState(false);
  const { control, handleSubmit, setError, formState } = useForm({
    resolver: yupResolver(schema),
    defaultValues: { new_password: '', confirm: '' },
  });
  const onSubmit = async ({ new_password }) => {
    try {
      await authApi.reset({ uid, token, new_password });
      setDone(true);
    } catch (err) {
      if (!applyFieldErrors(err, setError)) setError('root', { message: errorMessage(err) });
    }
  };
  return (
    <AuthCard title="Choose a new password">
      {done ? (
        <>
          <Alert severity="success">Password updated.</Alert>
          <Button component={RouterLink} to="/login" variant="contained" sx={{ mt: 2 }}>
            Sign in
          </Button>
        </>
      ) : (
        <Stack component="form" spacing={2} onSubmit={handleSubmit(onSubmit)} noValidate>
          {formState.errors.root && <Alert severity="error">{formState.errors.root.message}</Alert>}
          <RHFText control={control} name="new_password" label="New password" type="password" />
          <RHFText control={control} name="confirm" label="Repeat password" type="password" />
          <Button type="submit" variant="contained" disabled={formState.isSubmitting}>
            Save password
          </Button>
        </Stack>
      )}
    </AuthCard>
  );
}
