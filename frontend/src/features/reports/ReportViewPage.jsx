import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Button, LinearProgress } from '@mui/material';
import DownloadIcon from '@mui/icons-material/Download';
import { useSnackbar } from 'notistack';
import { reportsApi } from '../../api/endpoints';
import { download, errorMessage } from '../../api/client';
import { date, dateTime, PageHeader } from '../../components/common';
import ReportResult from './ReportResult';

export default function ReportViewPage() {
  const { id } = useParams();
  const { enqueueSnackbar } = useSnackbar();
  const [snap, setSnap] = useState(null);

  useEffect(() => {
    reportsApi
      .get(id)
      .then(setSnap)
      .catch((e) => enqueueSnackbar(errorMessage(e), { variant: 'error' }));
  }, [id, enqueueSnackbar]);

  const exportAs = (format) =>
    download(`/reports/${id}/export/`, { format }, `report.${format}`).catch((e) =>
      enqueueSnackbar(errorMessage(e), { variant: 'error' }),
    );

  if (!snap) return <LinearProgress />;
  const c = snap.criteria;
  return (
    <>
      <PageHeader
        title={snap.name}
        subtitle={`${date(c.date_from)} to ${date(c.date_to)}, grouped by ${c.group_by}. Generated ${dateTime(snap.generated_at)} by ${snap.owner.email}.`}
        actions={['csv', 'xlsx', 'json'].map((f) => (
          <Button key={f} startIcon={<DownloadIcon />} onClick={() => exportAs(f)} data-cy={`export-${f}`}>
            {f.toUpperCase()}
          </Button>
        ))}
      />
      <ReportResult rows={snap.rows} totals={snap.totals} />
    </>
  );
}
