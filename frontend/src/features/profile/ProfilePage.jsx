import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { useDispatch, useSelector } from 'react-redux';
import { Alert, Button, Grid2 as Grid, Paper, Stack, Typography } from '@mui/material';
import { useSnackbar } from 'notistack';
import { RHFText } from '../../components/FormFields';
import { PageHeader } from '../../components/common';
import { applyFieldErrors, errorMessage } from '../../api/client';
import { authApi } from '../../api/endpoints';
import { profileUpdated, selectUser } from '../auth/authSlice';

const pwdSchema = yup.object({
  current_password: yup.string().required('Required'),
  new_password: yup.string().min(10, 'At least 10 characters').required('Required'),
  confirm: yup.string().oneOf([yup.ref('new_password')], 'Passwords do not match'),
});

export default function ProfilePage() {
  const user = useSelector(selectUser);
  const dispatch = useDispatch();
  const { enqueueSnackbar } = useSnackbar();
  const profile = useForm({ defaultValues: { first_name: user.first_name, last_name: user.last_name } });
  const pwd = useForm({
    resolver: yupResolver(pwdSchema),
    defaultValues: { current_password: '', new_password: '', confirm: '' },
  });

  const saveProfile = async (values) => {
    try {
      dispatch(profileUpdated(await authApi.updateMe(values)));
      enqueueSnackbar('Profile saved', { variant: 'success' });
    } catch (err) {
      applyFieldErrors(err, profile.setError);
    }
  };

  const changePassword = async ({ current_password, new_password }) => {
    try {
      await authApi.changePassword({ current_password, new_password });
      pwd.reset();
      enqueueSnackbar('Password changed. Other sessions were signed out.', { variant: 'success' });
    } catch (err) {
      if (!applyFieldErrors(err, pwd.setError)) pwd.setError('root', { message: errorMessage(err) });
    }
  };

  return (
    <>
      <PageHeader
        title="Profile"
        subtitle={`${user.email} · ${user.role}${user.department_name ? ` · ${user.department_name}` : ''}`}
      />
      <Grid container spacing={2}>
        <Grid size={{ xs: 12, md: 6 }}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="subtitle1" gutterBottom>
              Your details
            </Typography>
            <Stack component="form" spacing={2} onSubmit={profile.handleSubmit(saveProfile)}>
              <RHFText control={profile.control} name="first_name" label="First name" />
              <RHFText control={profile.control} name="last_name" label="Last name" />
              <Button type="submit" variant="contained" sx={{ alignSelf: 'flex-end' }}>
                Save
              </Button>
            </Stack>
          </Paper>
        </Grid>
        <Grid size={{ xs: 12, md: 6 }}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="subtitle1" gutterBottom>
              Change password
            </Typography>
            <Stack component="form" spacing={2} onSubmit={pwd.handleSubmit(changePassword)} noValidate>
              {pwd.formState.errors.root && (
                <Alert severity="error">{pwd.formState.errors.root.message}</Alert>
              )}
              <RHFText
                control={pwd.control}
                name="current_password"
                label="Current password"
                type="password"
              />
              <RHFText control={pwd.control} name="new_password" label="New password" type="password" />
              <RHFText control={pwd.control} name="confirm" label="Repeat new password" type="password" />
              <Button type="submit" variant="contained" sx={{ alignSelf: 'flex-end' }}>
                Change password
              </Button>
            </Stack>
          </Paper>
        </Grid>
      </Grid>
    </>
  );
}
