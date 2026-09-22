import { useCallback, useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { Button, FormControlLabel, MenuItem, Paper, Stack, Switch, TextField } from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import AddIcon from '@mui/icons-material/Add';
import { useSnackbar } from 'notistack';
import { expensesApi } from '../../api/endpoints';
import { errorMessage } from '../../api/client';
import { date, EXPENSE_TYPES, money, PageHeader, STATUSES, StatusChip } from '../../components/common';
import { hasRole, selectUser } from '../auth/authSlice';

const columns = [
  { field: 'expense_date', headerName: 'Date', width: 120, valueFormatter: (v) => date(v) },
  { field: 'type', headerName: 'Type', width: 110 },
  { field: 'description', headerName: 'Description', flex: 1, minWidth: 200, sortable: false },
  { field: 'project_code', headerName: 'Project', width: 100, sortable: false },
  { field: 'employee_name', headerName: 'Employee', width: 160, sortable: false },
  { field: 'amount', headerName: 'Amount', width: 120, type: 'number', valueFormatter: (v) => money(v) },
  { field: 'status', headerName: 'Status', width: 130, renderCell: (p) => <StatusChip status={p.value} /> },
];

export default function ExpenseListPage() {
  const navigate = useNavigate();
  const user = useSelector(selectUser);
  const { enqueueSnackbar } = useSnackbar();
  const [filters, setFilters] = useState({
    status: '',
    type: '',
    q: '',
    date_from: '',
    date_to: '',
    mine: true,
  });
  const [paging, setPaging] = useState({ page: 0, pageSize: 20 });
  const [sort, setSort] = useState([{ field: 'expense_date', sort: 'desc' }]);
  const [data, setData] = useState({ rows: [], count: 0, loading: true });

  const load = useCallback(async () => {
    setData((d) => ({ ...d, loading: true }));
    const params = { page: paging.page + 1, page_size: paging.pageSize };
    Object.entries(filters).forEach(([k, v]) => {
      if (v !== '' && v !== false) params[k] = v;
    });
    if (sort[0]) params.ordering = `${sort[0].sort === 'desc' ? '-' : ''}${sort[0].field}`;
    try {
      const res = await expensesApi.list(params);
      setData({ rows: res.results, count: res.count, loading: false });
    } catch (err) {
      enqueueSnackbar(errorMessage(err), { variant: 'error' });
      setData((d) => ({ ...d, loading: false }));
    }
  }, [filters, paging, sort, enqueueSnackbar]);

  useEffect(() => {
    const t = setTimeout(load, 250); // debounce typing in the search box
    return () => clearTimeout(t);
  }, [load]);

  const set = (k) => (e) => {
    setPaging((p) => ({ ...p, page: 0 }));
    setFilters((f) => ({ ...f, [k]: e.target.type === 'checkbox' ? e.target.checked : e.target.value }));
  };

  return (
    <>
      <PageHeader
        title="Expenses"
        subtitle="Search, filter and open any expense you can see."
        actions={[
          <Button key="i" component={Link} to="/expenses/import">
            Import
          </Button>,
          <Button
            key="n"
            component={Link}
            to="/expenses/new"
            variant="contained"
            startIcon={<AddIcon />}
            data-cy="new-expense"
          >
            New expense
          </Button>,
        ]}
      />
      <Paper sx={{ p: 2, mb: 2 }}>
        <Stack direction={{ xs: 'column', md: 'row' }} spacing={2}>
          <TextField
            label="Search description"
            value={filters.q}
            onChange={set('q')}
            size="small"
            sx={{ flex: 2 }}
            inputProps={{ 'data-cy': 'search' }}
          />
          <TextField
            select
            label="Status"
            value={filters.status}
            onChange={set('status')}
            size="small"
            sx={{ minWidth: 150 }}
          >
            <MenuItem value="">All</MenuItem>
            {STATUSES.map((s) => (
              <MenuItem key={s} value={s}>
                {s}
              </MenuItem>
            ))}
          </TextField>
          <TextField
            select
            label="Type"
            value={filters.type}
            onChange={set('type')}
            size="small"
            sx={{ minWidth: 140 }}
          >
            <MenuItem value="">All</MenuItem>
            {EXPENSE_TYPES.map((s) => (
              <MenuItem key={s} value={s}>
                {s}
              </MenuItem>
            ))}
          </TextField>
          <TextField
            type="date"
            label="From"
            value={filters.date_from}
            onChange={set('date_from')}
            size="small"
            InputLabelProps={{ shrink: true }}
          />
          <TextField
            type="date"
            label="To"
            value={filters.date_to}
            onChange={set('date_to')}
            size="small"
            InputLabelProps={{ shrink: true }}
          />
          {hasRole(user, 'MANAGER', 'ADMIN') && (
            <FormControlLabel
              control={<Switch checked={filters.mine} onChange={set('mine')} />}
              label="Only mine"
            />
          )}
        </Stack>
      </Paper>
      <Paper sx={{ height: 640 }}>
        <DataGrid
          rows={data.rows}
          columns={columns}
          rowCount={data.count}
          loading={data.loading}
          paginationMode="server"
          sortingMode="server"
          paginationModel={paging}
          onPaginationModelChange={setPaging}
          sortModel={sort}
          onSortModelChange={setSort}
          pageSizeOptions={[10, 20, 50]}
          onRowClick={(p) => navigate(`/expenses/${p.id}`)}
          disableRowSelectionOnClick
          disableColumnFilter
          sx={{ border: 0, '& .MuiDataGrid-row': { cursor: 'pointer' } }}
        />
      </Paper>
    </>
  );
}
