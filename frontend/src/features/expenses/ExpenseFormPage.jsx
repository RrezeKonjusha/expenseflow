import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useForm, useWatch } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import { Alert, Button, Grid2 as Grid, LinearProgress, Paper, Stack } from '@mui/material';
import { useSnackbar } from 'notistack';
import dayjs from 'dayjs';
import { RHFText } from '../../components/FormFields';
import { PageHeader } from '../../components/common';
import { applyFieldErrors, errorMessage } from '../../api/client';
import { expensesApi, projectsApi } from '../../api/endpoints';
import { expenseSchema, POLICY } from './schemas';

const TYPE_OPTIONS = [
  { value: 'MEAL', label: 'Meal' },
  { value: 'TRAVEL', label: 'Travel' },
  { value: 'EQUIPMENT', label: 'Equipment' },
];

const EMPTY = {
  type: 'MEAL',
  project: '',
  amount: '',
  expense_date: dayjs().format('YYYY-MM-DD'),
  description: '',
  attendees: 1,
  distance_km: '',
  destination: '',
  item_name: '',
  serial_no: '',
};

export default function ExpenseFormPage() {
  const { id } = useParams();
  const editing = !!id;
  const navigate = useNavigate();
  const { enqueueSnackbar } = useSnackbar();
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const { control, handleSubmit, reset, setError, formState } = useForm({
    resolver: yupResolver(expenseSchema),
    mode: 'onBlur',
    defaultValues: EMPTY,
  });
  const type = useWatch({ control, name: 'type' });

  useEffect(() => {
    const jobs = [projectsApi.list({ is_active: true }).then(setProjects)];
    if (editing)
      jobs.push(
        expensesApi
          .get(id)
          .then((e) =>
            reset({ ...EMPTY, ...Object.fromEntries(Object.entries(e).filter(([, v]) => v !== null)) }),
          ),
      );
    Promise.all(jobs)
      .catch((err) => enqueueSnackbar(errorMessage(err), { variant: 'error' }))
      .finally(() => setLoading(false));
  }, [id, editing, reset, enqueueSnackbar]);

  const onSubmit = async (values) => {
    try {
      const saved = editing ? await expensesApi.update(id, values) : await expensesApi.create(values);
      enqueueSnackbar(editing ? 'Expense updated' : 'Draft saved', { variant: 'success' });
      navigate(`/expenses/${saved.id}`);
    } catch (err) {
      applyFieldErrors(err, setError); // field-level messages from the server policy check
      setError('root', { message: errorMessage(err) });
    }
  };

  if (loading) return <LinearProgress />;

  return (
    <>
      <PageHeader
        title={editing ? 'Edit expense' : 'New expense'}
        subtitle="Saved as a draft. Submit it from the detail page."
      />
      <Paper sx={{ p: 3, maxWidth: 860 }}>
        <Stack component="form" spacing={2} onSubmit={handleSubmit(onSubmit)} noValidate>
          {formState.errors.root && <Alert severity="error">{formState.errors.root.message}</Alert>}
          {projects.length === 0 && (
            <Alert severity="warning">You are not a member of any project yet. Ask an admin.</Alert>
          )}
          <Grid container spacing={2}>
            <Grid size={{ xs: 12, sm: 4 }}>
              <RHFText
                control={control}
                name="type"
                label="Type"
                select
                options={TYPE_OPTIONS}
                disabled={editing}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 8 }}>
              <RHFText
                control={control}
                name="project"
                label="Project"
                select
                options={projects.map((p) => ({ value: p.id, label: `${p.code} · ${p.name}` }))}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 4 }}>
              <RHFText
                control={control}
                name="amount"
                label="Amount (EUR)"
                type="number"
                inputProps={{ step: '0.01', min: 0, 'data-cy': 'amount' }}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 4 }}>
              <RHFText
                control={control}
                name="expense_date"
                label="Date"
                type="date"
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            {type === 'MEAL' && (
              <Grid size={{ xs: 12, sm: 4 }}>
                <RHFText
                  control={control}
                  name="attendees"
                  label="Attendees"
                  type="number"
                  helperText={`Max ${POLICY.mealCapPerAttendee} EUR per attendee`}
                />
              </Grid>
            )}
            {type === 'TRAVEL' && (
              <>
                <Grid size={{ xs: 12, sm: 4 }}>
                  <RHFText
                    control={control}
                    name="distance_km"
                    label="Distance (km)"
                    type="number"
                    helperText={`Max ${POLICY.travelRatePerKm} EUR per km`}
                  />
                </Grid>
                <Grid size={{ xs: 12, sm: 6 }}>
                  <RHFText control={control} name="destination" label="Destination" />
                </Grid>
              </>
            )}
            {type === 'EQUIPMENT' && (
              <>
                <Grid size={{ xs: 12, sm: 6 }}>
                  <RHFText control={control} name="item_name" label="Item" />
                </Grid>
                <Grid size={{ xs: 12, sm: 6 }}>
                  <RHFText
                    control={control}
                    name="serial_no"
                    label="Serial number"
                    helperText={`Max ${POLICY.equipmentMax} EUR`}
                  />
                </Grid>
              </>
            )}
            <Grid size={12}>
              <RHFText control={control} name="description" label="Description" multiline minRows={2} />
            </Grid>
          </Grid>
          <Stack direction="row" spacing={1} justifyContent="flex-end">
            <Button onClick={() => navigate(-1)}>Cancel</Button>
            <Button
              type="submit"
              variant="contained"
              disabled={formState.isSubmitting}
              data-cy="save-expense"
            >
              Save draft
            </Button>
          </Stack>
        </Stack>
      </Paper>
    </>
  );
}
