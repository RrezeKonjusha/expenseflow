import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { Link as RouterLink } from 'react-router-dom';
import { Alert, Button, Link, Stack } from '@mui/material';
import { RHFText } from '../../components/FormFields';
import { applyFieldErrors, errorMessage } from '../../api/client';
import { authApi } from '../../api/endpoints';
import AuthCard from './AuthCard';

const schema = yup.object({
  first_name: yup
    .string()
    .max(150)
    .matches(/^[^<>]*$/, 'No < or >'),
  last_name: yup
    .string()
    .max(150)
    .matches(/^[^<>]*$/, 'No < or >'),
  email: yup.string().email('Enter a valid email').required('Email is required'),
  password: yup
    .string()
    .min(10, 'At least 10 characters')
    .matches(/\D/, 'Cannot be only numbers')
    .required('Password is required'),
  confirm: yup
    .string()
    .oneOf([yup.ref('password')], 'Passwords do not match')
    .required('Repeat the password'),
});

export default function RegisterPage() {
  const [done, setDone] = useState(false);
  const { control, handleSubmit, setError, formState } = useForm({
    resolver: yupResolver(schema),
    mode: 'onBlur',
    defaultValues: { first_name: '', last_name: '', email: '', password: '', confirm: '' },
  });

  const onSubmit = async ({ confirm: _c, ...values }) => {
    try {
      await authApi.register(values);
      setDone(true);
    } catch (err) {
      if (!applyFieldErrors(err, setError)) setError('root', { message: errorMessage(err) });
    }
  };

  if (done) {
    return (
      <AuthCard title="Check your inbox">
        <Alert severity="success">We sent you an activation link. Open it to activate your account.</Alert>
        <Button component={RouterLink} to="/login" sx={{ mt: 2 }}>
          Back to sign in
        </Button>
      </AuthCard>
    );
  }

  return (
    <AuthCard title="Create account">
      <Stack component="form" spacing={2} onSubmit={handleSubmit(onSubmit)} noValidate>
        {formState.errors.root && <Alert severity="error">{formState.errors.root.message}</Alert>}
        <Stack direction="row" spacing={2}>
          <RHFText control={control} name="first_name" label="First name" />
          <RHFText control={control} name="last_name" label="Last name" />
        </Stack>
        <RHFText control={control} name="email" label="Work email" type="email" />
        <RHFText
          control={control}
          name="password"
          label="Password"
          type="password"
          helperText="At least 10 characters"
        />
        <RHFText control={control} name="confirm" label="Repeat password" type="password" />
        <Button
          type="submit"
          variant="contained"
          size="large"
          disabled={formState.isSubmitting}
          data-cy="register-submit"
        >
          Create account
        </Button>
        <Link component={RouterLink} to="/login">
          I already have an account
        </Link>
      </Stack>
    </AuthCard>
  );
}
