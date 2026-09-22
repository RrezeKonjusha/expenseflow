import { useCallback, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Paper,
  Stack,
  TextField,
} from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import { useSnackbar } from 'notistack';
import { useSelector } from 'react-redux';
import { expensesApi } from '../../api/endpoints';
import { errorMessage } from '../../api/client';
import { date, money, PageHeader } from '../../components/common';
import { selectUser } from '../auth/authSlice';

export default function ApprovalsPage() {
  const navigate = useNavigate();
  const user = useSelector(selectUser);
  const { enqueueSnackbar } = useSnackbar();
  const [q, setQ] = useState('');
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [rejecting, setRejecting] = useState(null);
  const [reason, setReason] = useState('');

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await expensesApi.list({
        status: 'SUBMITTED',
        q: q || undefined,
        page_size: 100,
        ordering: 'expense_date',
      });
      setRows(res.results.filter((e) => e.employee !== user.id));
    } catch (err) {
      enqueueSnackbar(errorMessage(err), { variant: 'error' });
    } finally {
      setLoading(false);
    }
  }, [q, user.id, enqueueSnackbar]);

  useEffect(() => {
    const t = setTimeout(load, 250);
    return () => clearTimeout(t);
  }, [load]);

  const act = async (id, name, body) => {
    try {
      await expensesApi.action(id, name, body);
      enqueueSnackbar(name === 'approve' ? 'Approved' : 'Rejected', { variant: 'success' });
      setRows((r) => r.filter((e) => e.id !== id));
      setRejecting(null);
      setReason('');
    } catch (err) {
      enqueueSnackbar(errorMessage(err), { variant: 'error' }); // e.g. "Project GAMMA budget would be exceeded"
    }
  };

  const columns = [
    { field: 'expense_date', headerName: 'Date', width: 115, valueFormatter: (v) => date(v) },
    { field: 'employee_name', headerName: 'Employee', width: 160 },
    { field: 'type', headerName: 'Type', width: 105 },
    { field: 'description', headerName: 'Description', flex: 1, minWidth: 180 },
    { field: 'project_code', headerName: 'Project', width: 90 },
    { field: 'amount', headerName: 'Amount', width: 110, type: 'number', valueFormatter: (v) => money(v) },
    {
      field: 'actions',
      headerName: '',
      width: 200,
      sortable: false,
      renderCell: (p) => (
        <Stack
          direction="row"
          spacing={1}
          sx={{ height: '100%', alignItems: 'center' }}
          onClick={(e) => e.stopPropagation()}
        >
          <Button
            size="small"
            variant="contained"
            color="success"
            onClick={() => act(p.id, 'approve')}
            data-cy={`approve-${p.id}`}
          >
            Approve
          </Button>
          <Button size="small" color="error" onClick={() => setRejecting(p.row)}>
            Reject
          </Button>
        </Stack>
      ),
    },
  ];

  return (
    <>
      <PageHeader title="Approvals" subtitle="Submitted expenses from your department, oldest first." />
      <Paper sx={{ p: 2, mb: 2 }}>
        <TextField
          size="small"
          fullWidth
          label="Search description"
          value={q}
          onChange={(e) => setQ(e.target.value)}
        />
      </Paper>
      <Paper sx={{ height: 600 }}>
        <DataGrid
          rows={rows}
          columns={columns}
          loading={loading}
          onRowClick={(p) => navigate(`/expenses/${p.id}`)}
          disableRowSelectionOnClick
          sx={{ border: 0 }}
          pageSizeOptions={[25, 50, 100]}
          initialState={{ pagination: { paginationModel: { pageSize: 25 } } }}
        />
      </Paper>
      <Dialog open={!!rejecting} onClose={() => setRejecting(null)} fullWidth maxWidth="sm">
        <DialogTitle>Reject {rejecting?.employee_name}&apos;s expense</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            fullWidth
            multiline
            minRows={2}
            label="Reason"
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            sx={{ mt: 1 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRejecting(null)}>Cancel</Button>
          <Button
            variant="contained"
            color="error"
            disabled={!reason.trim()}
            onClick={() => act(rejecting.id, 'reject', { reason })}
          >
            Reject
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
