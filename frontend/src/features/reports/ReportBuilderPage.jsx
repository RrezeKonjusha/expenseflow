import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useSelector } from 'react-redux';
import {
  Autocomplete,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Grid2 as Grid,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  MenuItem,
  Paper,
  Stack,
  TextField,
  Typography,
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/DeleteOutline';
import { useSnackbar } from 'notistack';
import dayjs from 'dayjs';
import { departmentsApi, expensesApi, projectsApi, reportsApi } from '../../api/endpoints';
import { errorMessage, fieldErrors } from '../../api/client';
import { EXPENSE_TYPES, money, PageHeader, STATUSES } from '../../components/common';
import { hasRole, selectUser } from '../auth/authSlice';
import ReportResult from './ReportResult';

const GROUPS = ['department', 'project', 'employee', 'type', 'status', 'month'];

export default function ReportBuilderPage() {
  const user = useSelector(selectUser);
  const { enqueueSnackbar } = useSnackbar();
  const [criteria, setCriteria] = useState({
    date_from: dayjs().subtract(3, 'month').startOf('month').format('YYYY-MM-DD'),
    date_to: dayjs().format('YYYY-MM-DD'),
    group_by: 'department',
    statuses: ['APPROVED', 'REIMBURSED'],
    types: [],
    department_ids: [],
    project_ids: [],
  });
  const [lookups, setLookups] = useState({ departments: [], projects: [] });
  const [result, setResult] = useState(null);
  const [errors, setErrors] = useState({});
  const [saved, setSaved] = useState([]);
  const [saveOpen, setSaveOpen] = useState(false);
  const [name, setName] = useState('');
  const [reimburseUntil, setReimburseUntil] = useState(dayjs().format('YYYY-MM-DD'));

  useEffect(() => {
    Promise.all([departmentsApi.list(), projectsApi.list()]).then(([departments, projects]) =>
      setLookups({ departments, projects }),
    );
    reportsApi.list().then(setSaved);
  }, []);

  const set = (k, v) => setCriteria((c) => ({ ...c, [k]: v }));

  const run = async () => {
    setErrors({});
    try {
      setResult(await reportsApi.run(criteria));
    } catch (err) {
      setErrors(fieldErrors(err));
      enqueueSnackbar(errorMessage(err), { variant: 'error' });
    }
  };

  const save = async () => {
    try {
      const snap = await reportsApi.save(name, criteria);
      setSaved((s) => [snap, ...s]);
      setSaveOpen(false);
      setName('');
      enqueueSnackbar('Report saved', { variant: 'success' });
    } catch (err) {
      enqueueSnackbar(errorMessage(err), { variant: 'error' });
    }
  };

  const remove = async (id) => {
    await reportsApi.remove(id);
    setSaved((s) => s.filter((r) => r.id !== id));
  };

  const reimburse = async () => {
    try {
      const { reimbursed } = await expensesApi.reimburse(reimburseUntil);
      enqueueSnackbar(`${reimbursed} expenses reimbursed`, { variant: 'success' });
    } catch (err) {
      enqueueSnackbar(errorMessage(err), { variant: 'error' });
    }
  };

  const multi = (key, options, label, getLabel = (o) => o) => (
    <Autocomplete
      multiple
      size="small"
      options={options}
      getOptionLabel={getLabel}
      value={options.filter((o) => criteria[key].includes(typeof o === 'object' ? o.id : o))}
      onChange={(_, v) =>
        set(
          key,
          v.map((o) => (typeof o === 'object' ? o.id : o)),
        )
      }
      renderInput={(p) => <TextField {...p} label={label} />}
    />
  );

  return (
    <>
      <PageHeader title="Reports" subtitle="Build a report from any criteria, save it, and export it." />
      <Grid container spacing={2}>
        <Grid size={{ xs: 12, lg: 8 }}>
          <Paper sx={{ p: 2.5, mb: 2 }}>
            <Grid container spacing={2}>
              <Grid size={{ xs: 6, md: 3 }}>
                <TextField
                  type="date"
                  size="small"
                  fullWidth
                  label="From"
                  value={criteria.date_from}
                  InputLabelProps={{ shrink: true }}
                  onChange={(e) => set('date_from', e.target.value)}
                />
              </Grid>
              <Grid size={{ xs: 6, md: 3 }}>
                <TextField
                  type="date"
                  size="small"
                  fullWidth
                  label="To"
                  value={criteria.date_to}
                  InputLabelProps={{ shrink: true }}
                  error={!!errors.date_to}
                  helperText={errors.date_to}
                  onChange={(e) => set('date_to', e.target.value)}
                />
              </Grid>
              <Grid size={{ xs: 12, md: 6 }}>
                <TextField
                  select
                  size="small"
                  fullWidth
                  label="Group by"
                  value={criteria.group_by}
                  onChange={(e) => set('group_by', e.target.value)}
                >
                  {GROUPS.map((g) => (
                    <MenuItem key={g} value={g}>
                      {g}
                    </MenuItem>
                  ))}
                </TextField>
              </Grid>
              <Grid size={{ xs: 12, md: 6 }}>{multi('statuses', STATUSES, 'Statuses')}</Grid>
              <Grid size={{ xs: 12, md: 6 }}>{multi('types', EXPENSE_TYPES, 'Types')}</Grid>
              <Grid size={{ xs: 12, md: 6 }}>
                {multi('department_ids', lookups.departments, 'Departments', (o) => o.name)}
              </Grid>
              <Grid size={{ xs: 12, md: 6 }}>
                {multi('project_ids', lookups.projects, 'Projects', (o) => o.code)}
              </Grid>
            </Grid>
            <Stack direction="row" spacing={1} sx={{ mt: 2 }} justifyContent="flex-end">
              <Button disabled={!result} onClick={() => setSaveOpen(true)}>
                Save report
              </Button>
              <Button variant="contained" onClick={run} data-cy="run-report">
                Run report
              </Button>
            </Stack>
          </Paper>
          {result && <ReportResult rows={result.rows} totals={result.totals} />}
        </Grid>
        <Grid size={{ xs: 12, lg: 4 }}>
          <Paper sx={{ p: 2.5, mb: 2 }}>
            <Typography variant="subtitle1">Saved reports</Typography>
            <List dense>
              {saved.length === 0 && (
                <Typography variant="body2" color="text.secondary">
                  Nothing saved yet.
                </Typography>
              )}
              {saved.map((s) => (
                <ListItem
                  key={s.id}
                  disablePadding
                  secondaryAction={
                    <IconButton edge="end" aria-label="Delete report" onClick={() => remove(s.id)}>
                      <DeleteIcon />
                    </IconButton>
                  }
                >
                  <ListItemButton component={Link} to={`/reports/${s.id}`}>
                    <ListItemText
                      primary={s.name}
                      secondary={`${s.criteria.group_by} · ${s.totals ? money(s.totals.total) : ''} · ${dayjs(s.generated_at).format('DD MMM')}`}
                    />
                  </ListItemButton>
                </ListItem>
              ))}
            </List>
          </Paper>
          {hasRole(user, 'ADMIN') && (
            <Paper sx={{ p: 2.5 }}>
              <Typography variant="subtitle1">Reimbursement run</Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Marks every approved expense up to the date as reimbursed (stored procedure).
              </Typography>
              <Stack direction="row" spacing={1}>
                <TextField
                  type="date"
                  size="small"
                  value={reimburseUntil}
                  onChange={(e) => setReimburseUntil(e.target.value)}
                />
                <Button variant="contained" onClick={reimburse} data-cy="reimburse">
                  Reimburse
                </Button>
              </Stack>
            </Paper>
          )}
        </Grid>
      </Grid>
      <Dialog open={saveOpen} onClose={() => setSaveOpen(false)} fullWidth maxWidth="xs">
        <DialogTitle>Save report</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            fullWidth
            label="Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            sx={{ mt: 1 }}
            inputProps={{ 'data-cy': 'report-name' }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSaveOpen(false)}>Cancel</Button>
          <Button variant="contained" disabled={!name.trim()} onClick={save} data-cy="save-report">
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
