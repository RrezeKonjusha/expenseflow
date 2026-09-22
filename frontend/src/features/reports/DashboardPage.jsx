import { useEffect, useState } from 'react';
import { useSelector } from 'react-redux';
import { Grid2 as Grid, Paper, Typography } from '@mui/material';
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import dayjs from 'dayjs';
import { reportsApi } from '../../api/endpoints';
import { money, PageHeader, StatCard } from '../../components/common';
import { selectUser } from '../auth/authSlice';

const SCOPE_TEXT = { all: 'All company data', department: 'Your department', user: 'Your own expenses' };

export default function DashboardPage() {
  const user = useSelector(selectUser);
  const [d, setD] = useState(null);

  useEffect(() => {
    reportsApi
      .dashboard()
      .then(setD)
      .catch(() => setD({ counts: {}, monthly: [], by_type: [] }));
  }, []);

  const monthly = (d?.monthly || []).map((m) => ({
    ...m,
    total: Number(m.total),
    label: dayjs(`${m.month}-01`).format('MMM'),
  }));
  const scope = d?.scope?.split(':')[0];

  return (
    <>
      <PageHeader title={`Hello, ${user.first_name || user.email}`} subtitle={SCOPE_TEXT[scope] || ''} />
      <Grid container spacing={2}>
        <Grid size={{ xs: 6, md: 3 }}>
          <StatCard
            label="Waiting for approval"
            value={d?.counts?.SUBMITTED}
            hint={d && money(d.pending_amount)}
          />
        </Grid>
        <Grid size={{ xs: 6, md: 3 }}>
          <StatCard
            label="Spent this month"
            value={d && money(d.spent_this_month)}
            hint="approved + reimbursed"
          />
        </Grid>
        <Grid size={{ xs: 6, md: 3 }}>
          <StatCard label="Drafts" value={d?.counts?.DRAFT} />
        </Grid>
        <Grid size={{ xs: 6, md: 3 }}>
          <StatCard label="Rejected" value={d?.counts?.REJECTED} />
        </Grid>
        <Grid size={{ xs: 12, md: 8 }}>
          <Paper sx={{ p: 2.5, height: 340 }}>
            <Typography variant="subtitle1" gutterBottom>
              Approved spend, last 6 months (EUR)
            </Typography>
            <ResponsiveContainer width="100%" height="88%">
              <BarChart data={monthly}>
                <CartesianGrid vertical={false} strokeDasharray="3 3" />
                <XAxis dataKey="label" tickLine={false} />
                <YAxis tickLine={false} axisLine={false} width={60} />
                <Tooltip formatter={(v) => money(v)} />
                <Bar dataKey="total" fill="#1565c0" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
        <Grid size={{ xs: 12, md: 4 }}>
          <Paper sx={{ p: 2.5, height: 340 }}>
            <Typography variant="subtitle1" gutterBottom>
              Spend by type
            </Typography>
            {(d?.by_type || []).map((t) => (
              <Typography
                key={t.type}
                sx={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  py: 1,
                  borderBottom: '1px solid #eee',
                }}
              >
                <span>{t.type}</span>
                <b>{money(t.total)}</b>
              </Typography>
            ))}
            {d?.generated_at && (
              <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 2 }}>
                Updated {dayjs(d.generated_at).format('HH:mm')} (cached up to 5 minutes)
              </Typography>
            )}
          </Paper>
        </Grid>
      </Grid>
    </>
  );
}
