import { useCallback, useEffect, useState } from 'react';
import { Dialog, DialogContent, DialogTitle, Paper, Stack, TextField, Typography } from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import { auditApi } from '../../api/endpoints';
import { dateTime, PageHeader } from '../../components/common';

const columns = [
  { field: 'ts', headerName: 'Time', width: 180, valueFormatter: (v) => dateTime(v) },
  { field: 'action', headerName: 'Action', width: 220 },
  {
    field: 'actor',
    headerName: 'Actor',
    flex: 1,
    minWidth: 200,
    valueGetter: (v) => (v ? `${v.email} (${v.role})` : 'system'),
  },
  { field: 'target', headerName: 'Target', width: 180, valueGetter: (v) => (v ? `${v.type} #${v.id}` : '') },
  { field: 'ip', headerName: 'IP', width: 130 },
];

export default function AuditPage() {
  const [filters, setFilters] = useState({ action: '', date_from: '', date_to: '' });
  const [paging, setPaging] = useState({ page: 0, pageSize: 25 });
  const [data, setData] = useState({ rows: [], count: 0, loading: true });
  const [open, setOpen] = useState(null);

  const load = useCallback(async () => {
    setData((d) => ({ ...d, loading: true }));
    const params = { page: paging.page + 1, page_size: paging.pageSize };
    Object.entries(filters).forEach(([k, v]) => v && (params[k] = v));
    const res = await auditApi.list(params);
    setData({ rows: res.results, count: res.count, loading: false });
  }, [filters, paging]);

  useEffect(() => {
    const t = setTimeout(load, 250);
    return () => clearTimeout(t);
  }, [load]);

  const set = (k) => (e) => setFilters((f) => ({ ...f, [k]: e.target.value }));

  return (
    <>
      <PageHeader
        title="Audit log"
        subtitle="Every critical action, stored in MongoDB. Click a row for details."
      />
      <Paper sx={{ p: 2, mb: 2 }}>
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
          <TextField
            size="small"
            label="Action (e.g. EXPENSE_APPROVED)"
            value={filters.action}
            onChange={set('action')}
            sx={{ flex: 1 }}
          />
          <TextField
            size="small"
            type="date"
            label="From"
            value={filters.date_from}
            onChange={set('date_from')}
            InputLabelProps={{ shrink: true }}
          />
          <TextField
            size="small"
            type="date"
            label="To"
            value={filters.date_to}
            onChange={set('date_to')}
            InputLabelProps={{ shrink: true }}
          />
        </Stack>
      </Paper>
      <Paper sx={{ height: 640 }}>
        <DataGrid
          rows={data.rows}
          columns={columns}
          rowCount={data.count}
          loading={data.loading}
          paginationMode="server"
          paginationModel={paging}
          onPaginationModelChange={setPaging}
          pageSizeOptions={[25, 50, 100]}
          onRowClick={(p) => setOpen(p.row)}
          disableRowSelectionOnClick
          sx={{ border: 0, '& .MuiDataGrid-row': { cursor: 'pointer' } }}
        />
      </Paper>
      <Dialog open={!!open} onClose={() => setOpen(null)} fullWidth maxWidth="sm">
        <DialogTitle>{open?.action}</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary">
            Request {open?.request_id}
          </Typography>
          <Typography
            component="pre"
            sx={{ bgcolor: '#f4f5f8', p: 2, borderRadius: 2, overflow: 'auto', fontSize: 13 }}
          >
            {JSON.stringify({ actor: open?.actor, target: open?.target, changes: open?.changes }, null, 2)}
          </Typography>
        </DialogContent>
      </Dialog>
    </>
  );
}
