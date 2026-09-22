import { useState } from 'react';
import {
  Alert,
  Button,
  Paper,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material';
import UploadIcon from '@mui/icons-material/UploadFile';
import { useSnackbar } from 'notistack';
import { expensesApi } from '../../api/endpoints';
import { errorMessage } from '../../api/client';
import { PageHeader } from '../../components/common';

const TEMPLATE =
  'type,project_code,amount,expense_date,description,distance_km,destination,attendees,item_name,serial_no\n' +
  'MEAL,ALPHA,40.00,2026-09-25,Team lunch,,,2,,\n' +
  'TRAVEL,ALPHA,30.00,2026-09-24,Client visit,80,Prizren,,,\n' +
  'EQUIPMENT,ALPHA,90.00,2026-09-23,Headset,,,,Headset,SN-1\n';

export default function ImportPage() {
  const { enqueueSnackbar } = useSnackbar();
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);

  const downloadTemplate = () => {
    const url = URL.createObjectURL(new Blob([TEMPLATE], { type: 'text/csv' }));
    const a = document.createElement('a');
    a.href = url;
    a.download = 'expenseflow-import-template.csv';
    a.click();
    URL.revokeObjectURL(url);
  };

  const upload = async () => {
    setBusy(true);
    try {
      const res = await expensesApi.importFile(file);
      setResult(res);
      enqueueSnackbar(`${res.created} drafts created`, {
        variant: res.errors.length ? 'warning' : 'success',
      });
    } catch (err) {
      enqueueSnackbar(errorMessage(err), { variant: 'error' });
    } finally {
      setBusy(false);
    }
  };

  return (
    <>
      <PageHeader
        title="Import expenses"
        subtitle="CSV or JSON, up to 500 rows. Valid rows become drafts; invalid rows are listed."
      />
      <Paper sx={{ p: 3, mb: 2 }}>
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} alignItems={{ sm: 'center' }}>
          <Button variant="outlined" component="label" startIcon={<UploadIcon />}>
            {file ? file.name : 'Choose file'}
            <input
              hidden
              type="file"
              accept=".csv,.json"
              data-cy="import-file"
              onChange={(e) => setFile(e.target.files[0])}
            />
          </Button>
          <Button variant="contained" disabled={!file || busy} onClick={upload} data-cy="import-submit">
            Import
          </Button>
          <Button onClick={downloadTemplate}>Download CSV template</Button>
        </Stack>
      </Paper>
      {result && (
        <Paper sx={{ p: 3 }}>
          <Alert severity={result.errors.length ? 'warning' : 'success'} sx={{ mb: 2 }}>
            {result.created} created, {result.errors.length} rows with errors.
          </Alert>
          {result.errors.length > 0 && (
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Row</TableCell>
                  <TableCell>Problems</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {result.errors.map((e) => (
                  <TableRow key={e.row}>
                    <TableCell>{e.row}</TableCell>
                    <TableCell>
                      {Object.entries(e.errors).map(([f, m]) => (
                        <Typography key={f} variant="body2">
                          <b>{f}</b>: {[].concat(m).join(' ')}
                        </Typography>
                      ))}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </Paper>
      )}
    </>
  );
}
