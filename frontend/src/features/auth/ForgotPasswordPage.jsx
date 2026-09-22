import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { Link as RouterLink } from 'react-router-dom';
import { Alert, Button, Link, Stack } from '@mui/material';
import { RHFText } from '../../components/FormFields';
import { authApi } from '../../api/endpoints';
import AuthCard from './AuthCard';

export default function ForgotPasswordPage() {
  const [sent, setSent] = useState(false);
  const { control, handleSubmit, formState } = useForm({
    resolver: yupResolver(yup.object({ email: yup.string().email().required('Email is required') })),
    defaultValues: { email: '' },
  });
  const onSubmit = async (values) => {
    await authApi.forgot(values).catch(() => null);
    setSent(true);
  };
  return (
    <AuthCard title="Reset password" subtitle="We will email you a reset link.">
      {sent ? (
        <Alert severity="info">If the email is registered, a reset link is on its way.</Alert>
      ) : (
        <Stack component="form" spacing={2} onSubmit={handleSubmit(onSubmit)} noValidate>
          <RHFText control={control} name="email" label="Email" type="email" />
          <Button type="submit" variant="contained" disabled={formState.isSubmitting}>
            Send link
          </Button>
        </Stack>
      )}
      <Link component={RouterLink} to="/login" sx={{ display: 'block', mt: 2 }}>
        Back to sign in
      </Link>
    </AuthCard>
  );
}
