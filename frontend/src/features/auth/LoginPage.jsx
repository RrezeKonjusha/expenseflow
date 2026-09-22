import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { useDispatch, useSelector } from 'react-redux';
import { Link as RouterLink, Navigate, useLocation, useNavigate } from 'react-router-dom';
import { Alert, Button, Link, Stack } from '@mui/material';
import { RHFText } from '../../components/FormFields';

import { login, selectStatus } from './authSlice';
import AuthCard from './AuthCard';

const schema = yup.object({
  email: yup.string().email('Enter a valid email').required('Email is required'),
  password: yup.string().required('Password is required'),
});

export default function LoginPage() {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const location = useLocation();
  const status = useSelector(selectStatus);
  const { control, handleSubmit, setError, formState } = useForm({
    resolver: yupResolver(schema),
    defaultValues: { email: '', password: '' },
  });

  if (status === 'authenticated') return <Navigate to="/" replace />;

  const onSubmit = async (values) => {
    try {
      await dispatch(login(values)).unwrap();
      navigate(location.state?.from?.pathname || '/', { replace: true });
    } catch (err) {
      const msg = err?.message?.includes('429') ? 'Too many attempts. Wait a minute and try again.' : null;
      setError('root', { message: msg || 'Wrong email or password, or the account is not activated yet.' });
    }
  };

  return (
    <AuthCard title="Sign in" subtitle="Submit and approve expenses in one place.">
      <Stack component="form" spacing={2} onSubmit={handleSubmit(onSubmit)} noValidate>
        {formState.errors.root && <Alert severity="error">{formState.errors.root.message}</Alert>}
        <RHFText control={control} name="email" label="Email" type="email" autoComplete="email" autoFocus />
        <RHFText
          control={control}
          name="password"
          label="Password"
          type="password"
          autoComplete="current-password"
        />
        <Button
          type="submit"
          variant="contained"
          size="large"
          disabled={formState.isSubmitting}
          data-cy="login-submit"
        >
          Sign in
        </Button>
        <Stack direction="row" justifyContent="space-between">
          <Link component={RouterLink} to="/register">
            Create account
          </Link>
          <Link component={RouterLink} to="/forgot-password">
            Forgot password?
          </Link>
        </Stack>
      </Stack>
    </AuthCard>
  );
}
