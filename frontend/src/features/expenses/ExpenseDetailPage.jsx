import { useCallback, useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import {
  Alert,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Divider,
  Grid2 as Grid,
  LinearProgress,
  Paper,
  Stack,
  TextField,
  Typography,
} from '@mui/material';
import { useSnackbar } from 'notistack';
import { expensesApi } from '../../api/endpoints';
import { errorMessage } from '../../api/client';
import ConfirmDialog from '../../components/ConfirmDialog';
import { date, dateTime, money, PageHeader, StatusChip } from '../../components/common';

function Field({ label, value }) {
  return (
    <Grid size={{ xs: 12, sm: 6, md: 4 }}>
      <Typography variant="caption" color="text.secondary">
        {label}
      </Typography>
      <Typography>{value ?? '-'}</Typography>
    </Grid>
  );
}

export default function ExpenseDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { enqueueSnackbar } = useSnackbar();
  const [expense, setExpense] = useState(null);
  const [busy, setBusy] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [rejecting, setRejecting] = useState(false);
  const [reason, setReason] = useState('');

  const load = useCallback(
    () =>
      expensesApi
        .get(id)
        .then(setExpense)
        .catch((e) => enqueueSnackbar(errorMessage(e), { variant: 'error' })),
    [id, enqueueSnackbar],
  );
  useEffect(() => {
    load();
  }, [load]);

  const run = async (name, body, message) => {
    setBusy(true);
    try {
      setExpense(await expensesApi.action(id, name, body));
      enqueueSnackbar(message, { variant: 'success' });
      setRejecting(false);
    } catch (err) {
      enqueueSnackbar(errorMessage(err), { variant: 'error' });
    } finally {
      setBusy(false);
    }
  };

  const remove = async () => {
    await expensesApi.remove(id);
    enqueueSnackbar('Draft deleted', { variant: 'success' });
    navigate('/expenses');
  };

  if (!expense) return <LinearProgress />;
  const links = expense._links || {};

  return (
    <>
      <PageHeader
        title={`${expense.type} expense #${expense.id}`}
        subtitle={expense.description}
        actions={[
          links.update && (
            <Button key="e" component={Link} to={`/expenses/${id}/edit`}>
              Edit
            </Button>
          ),
          links.delete && (
            <Button key="d" color="error" onClick={() => setConfirmDelete(true)}>
              Delete
            </Button>
          ),
          links.reopen && (
            <Button key="o" onClick={() => run('reopen', null, 'Back to draft')}>
              Reopen
            </Button>
          ),
          links.submit && (
            <Button
              key="s"
              variant="contained"
              disabled={busy}
              onClick={() => run('submit', null, 'Submitted for approval')}
              data-cy="submit-expense"
            >
              Submit
            </Button>
          ),
          links.reject && (
            <Button key="r" color="error" onClick={() => setRejecting(true)} data-cy="reject-expense">
              Reject
            </Button>
          ),
          links.approve && (
            <Button
              key="a"
              variant="contained"
              color="success"
              disabled={busy}
              onClick={() => run('approve', null, 'Approved')}
              data-cy="approve-expense"
            >
              Approve
            </Button>
          ),
        ].filter(Boolean)}
      />
      <Paper sx={{ p: 3 }}>
        <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 2 }}>
          <StatusChip status={expense.status} size="medium" />
          <Typography variant="h5">{money(expense.amount)}</Typography>
          {expense.reimbursable_amount !== expense.amount && (
            <Typography color="text.secondary">reimbursable {money(expense.reimbursable_amount)}</Typography>
          )}
        </Stack>
        {expense.status === 'REJECTED' && (
          <Alert severity="error" sx={{ mb: 2 }}>
            Rejected: {expense.rejection_reason}
          </Alert>
        )}
        <Grid container spacing={2}>
          <Field label="Date" value={date(expense.expense_date)} />
          <Field label="Project" value={expense.project_code} />
          <Field
            label="Employee"
            value={`${expense.employee_name} (${expense.department_name || 'no department'})`}
          />
          {expense.type === 'MEAL' && <Field label="Attendees" value={expense.attendees} />}
          {expense.type === 'TRAVEL' && (
            <Field label="Distance" value={`${expense.distance_km} km to ${expense.destination}`} />
          )}
          {expense.type === 'EQUIPMENT' && (
            <Field label="Item" value={`${expense.item_name} (S/N ${expense.serial_no})`} />
          )}
        </Grid>
        <Divider sx={{ my: 3 }} />
        <Typography variant="subtitle2" gutterBottom>
          Timeline
        </Typography>
        <Stack spacing={0.5}>
          <Typography variant="body2">Created {dateTime(expense.created_at)}</Typography>
          {expense.submitted_at && (
            <Typography variant="body2">Submitted {dateTime(expense.submitted_at)}</Typography>
          )}
          {expense.decided_at && (
            <Typography variant="body2">
              {expense.status === 'REJECTED' ? 'Rejected' : 'Approved'} by {expense.decided_by_name}{' '}
              {dateTime(expense.decided_at)}
            </Typography>
          )}
          {expense.reimbursed_at && (
            <Typography variant="body2">Reimbursed {dateTime(expense.reimbursed_at)}</Typography>
          )}
        </Stack>
      </Paper>

      <ConfirmDialog
        open={confirmDelete}
        title="Delete draft?"
        message="This cannot be undone."
        confirmLabel="Delete"
        color="error"
        onConfirm={remove}
        onClose={() => setConfirmDelete(false)}
      />
      <Dialog open={rejecting} onClose={() => setRejecting(false)} fullWidth maxWidth="sm">
        <DialogTitle>Reject expense</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            fullWidth
            multiline
            minRows={2}
            label="Reason (shown to the employee)"
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            sx={{ mt: 1 }}
            inputProps={{ 'data-cy': 'reject-reason' }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRejecting(false)}>Cancel</Button>
          <Button
            variant="contained"
            color="error"
            disabled={!reason.trim() || busy}
            onClick={() => run('reject', { reason }, 'Rejected')}
          >
            Reject
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
