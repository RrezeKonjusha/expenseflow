import { lazy, Suspense } from 'react';
import { createBrowserRouter } from 'react-router-dom';
import { LinearProgress } from '@mui/material';
import AppLayout from '../components/AppLayout';
import RequireAuth from '../components/RequireAuth';

// Every page is lazy-loaded: only the code for the current route is downloaded.
const page = (loader) => {
  const Component = lazy(loader);
  return (
    <Suspense fallback={<LinearProgress />}>
      <Component />
    </Suspense>
  );
};

export const router = createBrowserRouter([
  { path: '/login', element: page(() => import('../features/auth/LoginPage')) },
  { path: '/register', element: page(() => import('../features/auth/RegisterPage')) },
  { path: '/activate/:uid/:token', element: page(() => import('../features/auth/ActivatePage')) },
  { path: '/forgot-password', element: page(() => import('../features/auth/ForgotPasswordPage')) },
  { path: '/reset-password/:uid/:token', element: page(() => import('../features/auth/ResetPasswordPage')) },
  {
    element: <RequireAuth />,
    children: [
      {
        element: <AppLayout />,
        children: [
          { index: true, element: page(() => import('../features/reports/DashboardPage')) },
          { path: 'expenses', element: page(() => import('../features/expenses/ExpenseListPage')) },
          { path: 'expenses/new', element: page(() => import('../features/expenses/ExpenseFormPage')) },
          { path: 'expenses/import', element: page(() => import('../features/expenses/ImportPage')) },
          { path: 'expenses/:id', element: page(() => import('../features/expenses/ExpenseDetailPage')) },
          { path: 'expenses/:id/edit', element: page(() => import('../features/expenses/ExpenseFormPage')) },
          { path: 'reports', element: page(() => import('../features/reports/ReportBuilderPage')) },
          { path: 'reports/:id', element: page(() => import('../features/reports/ReportViewPage')) },
          { path: 'profile', element: page(() => import('../features/profile/ProfilePage')) },
          {
            element: <RequireAuth roles={['MANAGER', 'ADMIN']} />,
            children: [
              { path: 'approvals', element: page(() => import('../features/approvals/ApprovalsPage')) },
            ],
          },
          {
            path: 'admin',
            element: <RequireAuth roles={['ADMIN']} />,
            children: [
              { path: 'users', element: page(() => import('../features/admin/UsersPage')) },
              { path: 'departments', element: page(() => import('../features/admin/DepartmentsPage')) },
              { path: 'projects', element: page(() => import('../features/admin/ProjectsPage')) },
              { path: 'audit', element: page(() => import('../features/admin/AuditPage')) },
            ],
          },
          { path: '*', element: page(() => import('../components/NotFoundPage')) },
        ],
      },
    ],
  },
]);
