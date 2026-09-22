import { useCallback, useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import {
  Alert,
  Button,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  MenuItem,
  Paper,
  Stack,
  TextField,
} from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import AddIcon from '@mui/icons-material/PersonAdd';
import { useSnackbar } from 'notistack';
import { departmentsApi, usersApi } from '../../api/endpoints';
import { applyFieldErrors, errorMessage } from '../../api/client';
import { RHFText } from '../../components/FormFields';
import ConfirmDialog from '../../components/ConfirmDialog';
import { date, PageHeader } from '../../components/common';

const ROLES = ['USER', 'MANAGER', 'ADMIN'].map((r) => ({ value: r, label: r }));

const schema = (creating) =>
  yup.object({
    email: yup.string().email().required(),
    first_name: yup.string().max(150),
    last_name: yup.string().max(150),
    role: yup.string().required(),
    department: yup.mixed().nullable(),
    password: creating ? yup.string().min(10, 'At least 10 characters').required() : yup.string(),
  });

function UserDialog({ user, departments, onClose, onSaved }) {
  const creating = !user?.id;
  const { control, handleSubmit, setError, formState } = useForm({
    resolver: yupResolver(schema(creating)),
    defaultValues: {
      email: '',
      first_name: '',
      last_name: '',
      role: 'USER',
      department: '',
      password: '',
      ...user,
    },
  });
  const onSubmit = async (values) => {
    const body = { ...values, department: values.department || null };
    if (!body.password) delete body.password;
    try {
      const saved = creating ? await usersApi.create(body) : await usersApi.update(user.id, body);
      onSaved(saved);
    } catch (err) {
      if (!applyFieldErrors(err, setError)) setError('root', { message: errorMessage(err) });
    }
  };
  return (
    <Dialog open onClose={onClose} fullWidth maxWidth="sm">
      <form onSubmit={handleSubmit(onSubmit)} noValidate>
        <DialogTitle>{creating ? 'New user' : `Edit ${user.email}`}</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            {formState.errors.root && <Alert severity="error">{formState.errors.root.message}</Alert>}
            <RHFText control={control} name="email" label="Email" disabled={!creating} />
            <Stack direction="row" spacing={2}>
              <RHFText control={control} name="first_name" label="First name" />
              <RHFText control={control} name="last_name" label="Last name" />
            </Stack>
            <Stack direction="row" spacing={2}>
              <RHFText control={control} name="role" label="Role" select options={ROLES} />
              <RHFText
                control={control}
                name="department"
                label="Department"
                select
                options={[
                  { value: '', label: 'None' },
                  ...departments.map((d) => ({ value: d.id, label: d.name })),
                ]}
              />
            </Stack>
            <RHFText
              control={control}
              name="password"
              label={creating ? 'Initial password' : 'New password (optional)'}
              type="password"
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose}>Cancel</Button>
          <Button type="submit" variant="contained" disabled={formState.isSubmitting}>
            Save
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
}

export default function UsersPage() {
  const { enqueueSnackbar } = useSnackbar();
  const [departments, setDepartments] = useState([]);
  const [search, setSearch] = useState('');
  const [role, setRole] = useState('');
  const [paging, setPaging] = useState({ page: 0, pageSize: 20 });
  const [data, setData] = useState({ rows: [], count: 0, loading: true });
  const [editing, setEditing] = useState(null);
  const [deactivating, setDeactivating] = useState(null);

  const load = useCallback(async () => {
    setData((d) => ({ ...d, loading: true }));
    const res = await usersApi.list({
      page: paging.page + 1,
      page_size: paging.pageSize,
      search: search || undefined,
      role: role || undefined,
    });
    setData({ rows: res.results, count: res.count, loading: false });
  }, [paging, search, role]);

  useEffect(() => {
    departmentsApi.list().then(setDepartments);
  }, []);
  useEffect(() => {
    const t = setTimeout(load, 250);
    return () => clearTimeout(t);
  }, [load]);

  const columns = [
    { field: 'email', headerName: 'Email', flex: 1, minWidth: 200 },
    { field: 'full_name', headerName: 'Name', width: 180 },
    { field: 'role', headerName: 'Role', width: 110 },
    { field: 'department_name', headerName: 'Department', width: 140 },
    {
      field: 'is_active',
      headerName: 'Status',
      width: 110,
      renderCell: (p) => (
        <Chip
          size="small"
          label={p.value ? 'Active' : 'Inactive'}
          color={p.value ? 'success' : 'default'}
          variant="outlined"
        />
      ),
    },
    { field: 'date_joined', headerName: 'Joined', width: 120, valueFormatter: (v) => date(v) },
    {
      field: 'actions',
      headerName: '',
      width: 170,
      sortable: false,
      renderCell: (p) => (
        <Stack direction="row" spacing={1} sx={{ height: '100%', alignItems: 'center' }}>
          <Button size="small" onClick={() => setEditing(p.row)}>
            Edit
          </Button>
          {p.row.is_active && (
            <Button size="small" color="error" onClick={() => setDeactivating(p.row)}>
              Deactivate
            </Button>
          )}
        </Stack>
      ),
    },
  ];

  return (
    <>
      <PageHeader
        title="Users"
        actions={
          <Button variant="contained" startIcon={<AddIcon />} onClick={() => setEditing({})}>
            New user
          </Button>
        }
      />
      <Paper sx={{ p: 2, mb: 2 }}>
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
          <TextField
            size="small"
            label="Search"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            sx={{ flex: 1 }}
          />
          <TextField
            size="small"
            select
            label="Role"
            value={role}
            onChange={(e) => setRole(e.target.value)}
            sx={{ minWidth: 150 }}
          >
            <MenuItem value="">All</MenuItem>
            {ROLES.map((r) => (
              <MenuItem key={r.value} value={r.value}>
                {r.label}
              </MenuItem>
            ))}
          </TextField>
        </Stack>
      </Paper>
      <Paper sx={{ height: 600 }}>
        <DataGrid
          rows={data.rows}
          columns={columns}
          rowCount={data.count}
          loading={data.loading}
          paginationMode="server"
          paginationModel={paging}
          onPaginationModelChange={setPaging}
          pageSizeOptions={[20, 50]}
          disableRowSelectionOnClick
          sx={{ border: 0 }}
        />
      </Paper>
      {editing && (
        <UserDialog
          user={editing}
          departments={departments}
          onClose={() => setEditing(null)}
          onSaved={() => {
            setEditing(null);
            enqueueSnackbar('User saved', { variant: 'success' });
            load();
          }}
        />
      )}
      <ConfirmDialog
        open={!!deactivating}
        title="Deactivate user?"
        message={`${deactivating?.email} will no longer be able to sign in.`}
        confirmLabel="Deactivate"
        color="error"
        onClose={() => setDeactivating(null)}
        onConfirm={async () => {
          await usersApi.deactivate(deactivating.id);
          setDeactivating(null);
          load();
        }}
      />
    </>
  );
}
