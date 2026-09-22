import { useCallback, useEffect, useState } from 'react';
import {
  Alert,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  MenuItem,
  Paper,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
} from '@mui/material';
import { useSnackbar } from 'notistack';
import { departmentsApi, usersApi } from '../../api/endpoints';
import { errorMessage, fieldErrors } from '../../api/client';
import ConfirmDialog from '../../components/ConfirmDialog';
import { PageHeader } from '../../components/common';

export default function DepartmentsPage() {
  const { enqueueSnackbar } = useSnackbar();
  const [rows, setRows] = useState([]);
  const [managers, setManagers] = useState([]);
  const [editing, setEditing] = useState(null);
  const [errors, setErrors] = useState({});
  const [deleting, setDeleting] = useState(null);

  const load = useCallback(() => departmentsApi.list().then(setRows), []);
  useEffect(() => {
    load();
    usersApi.list({ role: 'MANAGER', page_size: 100 }).then((r) => setManagers(r.results));
  }, [load]);

  const save = async () => {
    const body = { name: editing.name, manager: editing.manager || null };
    try {
      if (editing.id) await departmentsApi.update(editing.id, body);
      else await departmentsApi.create(body);
      setEditing(null);
      enqueueSnackbar('Department saved', { variant: 'success' });
      load();
    } catch (err) {
      setErrors(fieldErrors(err));
    }
  };

  return (
    <>
      <PageHeader
        title="Departments"
        actions={
          <Button
            variant="contained"
            onClick={() => {
              setErrors({});
              setEditing({ name: '', manager: '' });
            }}
          >
            New department
          </Button>
        }
      />
      <Paper>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Manager</TableCell>
              <TableCell align="right">Members</TableCell>
              <TableCell />
            </TableRow>
          </TableHead>
          <TableBody>
            {rows.map((d) => (
              <TableRow key={d.id} hover>
                <TableCell>{d.name}</TableCell>
                <TableCell>{d.manager_name || '-'}</TableCell>
                <TableCell align="right">{d.member_count}</TableCell>
                <TableCell align="right">
                  <Button
                    size="small"
                    onClick={() => {
                      setErrors({});
                      setEditing({ ...d, manager: d.manager || '' });
                    }}
                  >
                    Edit
                  </Button>
                  <Button size="small" color="error" onClick={() => setDeleting(d)}>
                    Delete
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Paper>
      <Dialog open={!!editing} onClose={() => setEditing(null)} fullWidth maxWidth="xs">
        <DialogTitle>{editing?.id ? 'Edit department' : 'New department'}</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            {errors.non_field_errors && <Alert severity="error">{errors.non_field_errors}</Alert>}
            <TextField
              label="Name"
              value={editing?.name || ''}
              error={!!errors.name}
              helperText={errors.name}
              onChange={(e) => setEditing({ ...editing, name: e.target.value })}
            />
            <TextField
              select
              label="Manager"
              value={editing?.manager ?? ''}
              error={!!errors.manager}
              helperText={errors.manager}
              onChange={(e) => setEditing({ ...editing, manager: e.target.value })}
            >
              <MenuItem value="">None</MenuItem>
              {managers.map((m) => (
                <MenuItem key={m.id} value={m.id}>
                  {m.full_name}
                </MenuItem>
              ))}
            </TextField>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditing(null)}>Cancel</Button>
          <Button variant="contained" onClick={save}>
            Save
          </Button>
        </DialogActions>
      </Dialog>
      <ConfirmDialog
        open={!!deleting}
        title="Delete department?"
        message="Members keep their accounts but lose the department."
        confirmLabel="Delete"
        color="error"
        onClose={() => setDeleting(null)}
        onConfirm={async () => {
          try {
            await departmentsApi.remove(deleting.id);
            load();
          } catch (e) {
            enqueueSnackbar(errorMessage(e), { variant: 'error' });
          }
          setDeleting(null);
        }}
      />
    </>
  );
}
