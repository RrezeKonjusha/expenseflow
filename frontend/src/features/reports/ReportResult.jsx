import { Paper, Table, TableBody, TableCell, TableHead, TableRow, Typography } from '@mui/material';
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { money } from '../../components/common';

export default function ReportResult({ rows, totals }) {
  const chart = rows.map((r) => ({ ...r, total: Number(r.total) }));
  return (
    <Paper sx={{ p: 2.5 }}>
      {rows.length === 0 ? (
        <Typography color="text.secondary">No expenses match these criteria.</Typography>
      ) : (
        <>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={chart}>
              <CartesianGrid vertical={false} strokeDasharray="3 3" />
              <XAxis
                dataKey="label"
                tickLine={false}
                interval={0}
                angle={rows.length > 6 ? -30 : 0}
                height={rows.length > 6 ? 60 : 30}
                textAnchor={rows.length > 6 ? 'end' : 'middle'}
              />
              <YAxis tickLine={false} axisLine={false} width={60} />
              <Tooltip formatter={(v) => money(v)} />
              <Bar dataKey="total" fill="#1565c0" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
          <Table size="small" sx={{ mt: 2 }}>
            <TableHead>
              <TableRow>
                <TableCell>Group</TableCell>
                <TableCell align="right">Count</TableCell>
                <TableCell align="right">Total</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {rows.map((r) => (
                <TableRow key={r.key}>
                  <TableCell>{r.label}</TableCell>
                  <TableCell align="right">{r.count}</TableCell>
                  <TableCell align="right">{money(r.total)}</TableCell>
                </TableRow>
              ))}
              <TableRow>
                <TableCell>
                  <b>Total</b>
                </TableCell>
                <TableCell align="right">
                  <b>{totals.count}</b>
                </TableCell>
                <TableCell align="right">
                  <b>{money(totals.total)}</b>
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </>
      )}
    </Paper>
  );
}
