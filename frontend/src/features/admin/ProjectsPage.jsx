import { useCallback, useEffect, useState } from 'react';
import {
  Autocomplete,
  Button,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControlLabel,
  LinearProgress,
  Paper,
  Stack,
  Switch,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from '@mui/material';
import { useSnackbar } from 'notistack';
import { projectsApi, usersApi } from '../../api/endpoints';
import { errorMessage, fieldErrors } from '../../api/client';
import { money, PageHeader } from '../../components/common';

export default function ProjectsPage() {
  const { enqueueSnackbar } = useSnackbar();
  const [rows, setRows] = useState([]);
  const [users, setUsers] = useState([]);
  const [editing, setEditing] = useState(null);
  const [errors, setErrors] = useState({});

  const load = useCallback(() => projectsApi.list().then(setRows), []);
  useEffect(() => {
    load();
    usersApi.list({ page_size: 100, is_active: true }).then((r) => setUsers(r.results));
  }, [load]);

  const save = async () => {
    const { id, code, name, budget, is_active, member_ids } = editing;
    try {
      const saved = id
        ? await projectsApi.update(id, { name, budget, is_active })
        : await projectsApi.create({ code, name, budget, is_active });
      await projectsApi.setMembers(saved.id, member_ids);
      setEditing(null);
      enqueueSnackbar('Project saved', { variant: 'success' });
      load();
    } catch (err) {
      setErrors(fieldErrors(err));
      enqueueSnackbar(errorMessage(err), { variant: 'error' });
    }
  };

  return (
    <>
      <PageHeader
        title="Projects"
        subtitle="Budgets are enforced by the database when expenses are approved."
        actions={
          <Button
            variant="contained"
            onClick={() => {
              setErrors({});
              setEditing({ code: '', name: '', budget: '', is_active: true, member_ids: [] });
            }}
          >
            New project
          </Button>
        }
      />
      <Paper>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Code</TableCell>
              <TableCell>Name</TableCell>
              <TableCell sx={{ minWidth: 220 }}>Budget used</TableCell>
              <TableCell align="right">Members</TableCell>
              <TableCell>Status</TableCell>
              <TableCell />
            </TableRow>
          </TableHead>
          <TableBody>
            {rows.map((p) => {
              const pct = Number(p.budget) ? Math.min(100, (Number(p.spent) / Number(p.budget)) * 100) : 0;
              return (
                <TableRow key={p.id} hover>
                  <TableCell>
                    <b>{p.code}</b>
                  </TableCell>
                  <TableCell>{p.name}</TableCell>
                  <TableCell>
                    <LinearProgress
                      variant="determinate"
                      value={pct}
                      color={pct > 90 ? 'error' : 'primary'}
                      sx={{ height: 8, borderRadius: 4 }}
                    />
                    <Typography variant="caption">
                      {money(p.spent)} of {money(p.budget)} ({pct.toFixed(0)}%)
                    </Typography>
                  </TableCell>
                  <TableCell align="right">{p.member_ids.length}</TableCell>
                  <TableCell>
                    <Chip size="small" label={p.is_active ? 'Active' : 'Closed'} variant="outlined" />
                  </TableCell>
                  <TableCell align="right">
                    <Button
                      size="small"
                      onClick={() => {
                        setErrors({});
                        setEditing({ ...p });
                      }}
                    >
                      Edit
                    </Button>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </Paper>
      <Dialog open={!!editing} onClose={() => setEditing(null)} fullWidth maxWidth="sm">
        <DialogTitle>{editing?.id ? `Edit ${editing.code}` : 'New project'}</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <Stack direction="row" spacing={2}>
              <TextField
                label="Code"
                value={editing?.code || ''}
                disabled={!!editing?.id}
                error={!!errors.code}
                helperText={errors.code || 'e.g. ALPHA'}
                onChange={(e) => setEditing({ ...editing, code: e.target.value.toUpperCase() })}
              />
              <TextField
                label="Budget (EUR)"
                type="number"
                value={editing?.budget || ''}
                error={!!errors.budget}
                helperText={errors.budget}
                onChange={(e) => setEditing({ ...editing, budget: e.target.value })}
              />
            </Stack>
            <TextField
              label="Name"
              value={editing?.name || ''}
              error={!!errors.name}
              helperText={errors.name}
              onChange={(e) => setEditing({ ...editing, name: e.target.value })}
            />
            <Autocomplete
              multiple
              options={users}
              getOptionLabel={(u) => `${u.full_name} (${u.email})`}
              value={users.filter((u) => editing?.member_ids?.includes(u.id))}
              onChange={(_, v) => setEditing({ ...editing, member_ids: v.map((u) => u.id) })}
              renderInput={(p) => <TextField {...p} label="Members" />}
            />
            <FormControlLabel
              control={
                <Switch
                  checked={!!editing?.is_active}
                  onChange={(e) => setEditing({ ...editing, is_active: e.target.checked })}
                />
              }
              label="Active"
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditing(null)}>Cancel</Button>
          <Button variant="contained" onClick={save}>
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
