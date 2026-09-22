import { useSelector } from 'react-redux';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { hasRole, selectStatus, selectUser } from '../features/auth/authSlice';

/** Guards a route subtree. `roles` limits it further (e.g. ['ADMIN']). */
export default function RequireAuth({ roles }) {
  const status = useSelector(selectStatus);
  const user = useSelector(selectUser);
  const location = useLocation();

  if (status !== 'authenticated') return <Navigate to="/login" replace state={{ from: location }} />;
  if (roles && !hasRole(user, ...roles)) return <Navigate to="/" replace />;
  return <Outlet />;
}
