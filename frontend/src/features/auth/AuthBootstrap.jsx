import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Box, CircularProgress } from '@mui/material';
import { bootstrap, selectStatus } from './authSlice';

export default function AuthBootstrap({ children }) {
  const dispatch = useDispatch();
  const status = useSelector(selectStatus);

  useEffect(() => {
    dispatch(bootstrap());
  }, [dispatch]);

  if (status === 'checking') {
    return (
      <Box sx={{ display: 'grid', placeItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }
  return children;
}
