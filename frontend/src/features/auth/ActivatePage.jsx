import { useEffect, useRef, useState } from 'react';
import { Link as RouterLink, useParams } from 'react-router-dom';
import { Alert, Button, CircularProgress } from '@mui/material';
import { authApi } from '../../api/endpoints';
import { errorMessage } from '../../api/client';
import AuthCard from './AuthCard';

export default function ActivatePage() {
  const { uid, token } = useParams();
  const [state, setState] = useState({ loading: true });
  const sent = useRef(false);

  useEffect(() => {
    if (sent.current) return; // StrictMode runs effects twice in dev; the token is single-use
    sent.current = true;
    authApi
      .activate({ uid, token })
      .then((r) => setState({ ok: true, message: r.detail }))
      .catch((e) => setState({ ok: false, message: errorMessage(e) }));
  }, [uid, token]);

  return (
    <AuthCard title="Account activation">
      {state.loading ? (
        <CircularProgress />
      ) : (
        <Alert severity={state.ok ? 'success' : 'error'}>{state.message}</Alert>
      )}
      <Button component={RouterLink} to="/login" variant="contained" sx={{ mt: 2 }}>
        Go to sign in
      </Button>
    </AuthCard>
  );
}
