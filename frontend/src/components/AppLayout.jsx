import { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import {
  AppBar,
  Avatar,
  Box,
  Chip,
  Divider,
  Drawer,
  IconButton,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  ListSubheader,
  Menu,
  MenuItem,
  Toolbar,
  Typography,
  useMediaQuery,
} from '@mui/material';
import { useTheme } from '@mui/material/styles';
import MenuIcon from '@mui/icons-material/Menu';
import DashboardIcon from '@mui/icons-material/SpaceDashboard';
import ReceiptIcon from '@mui/icons-material/ReceiptLong';
import UploadIcon from '@mui/icons-material/UploadFile';
import ApprovalIcon from '@mui/icons-material/FactCheck';
import ReportIcon from '@mui/icons-material/Assessment';
import PeopleIcon from '@mui/icons-material/People';
import ApartmentIcon from '@mui/icons-material/Apartment';
import WorkIcon from '@mui/icons-material/Work';
import HistoryIcon from '@mui/icons-material/History';
import { hasRole, logout, selectUser } from '../features/auth/authSlice';

const WIDTH = 240;

const NAV = [
  { section: 'Work' },
  { to: '/', label: 'Dashboard', icon: <DashboardIcon />, end: true },
  { to: '/expenses', label: 'My expenses', icon: <ReceiptIcon /> },
  { to: '/expenses/import', label: 'Import', icon: <UploadIcon /> },
  { to: '/approvals', label: 'Approvals', icon: <ApprovalIcon />, roles: ['MANAGER', 'ADMIN'] },
  { to: '/reports', label: 'Reports', icon: <ReportIcon /> },
  { section: 'Administration', roles: ['ADMIN'] },
  { to: '/admin/users', label: 'Users', icon: <PeopleIcon />, roles: ['ADMIN'] },
  { to: '/admin/departments', label: 'Departments', icon: <ApartmentIcon />, roles: ['ADMIN'] },
  { to: '/admin/projects', label: 'Projects', icon: <WorkIcon />, roles: ['ADMIN'] },
  { to: '/admin/audit', label: 'Audit log', icon: <HistoryIcon />, roles: ['ADMIN'] },
];

export default function AppLayout() {
  const theme = useTheme();
  const desktop = useMediaQuery(theme.breakpoints.up('md'));
  const [open, setOpen] = useState(false);
  const [anchor, setAnchor] = useState(null);
  const user = useSelector(selectUser);
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const items = NAV.filter((i) => !i.roles || hasRole(user, ...i.roles));
  const drawer = (
    <Box sx={{ width: WIDTH }} role="navigation">
      <Toolbar>
        <Typography variant="h6" fontWeight={700} color="primary">
          ExpenseFlow
        </Typography>
      </Toolbar>
      <Divider />
      <List dense>
        {items.map((item) =>
          item.section ? (
            <ListSubheader key={item.section}>{item.section}</ListSubheader>
          ) : (
            <ListItemButton
              key={item.to}
              component={NavLink}
              to={item.to}
              end={item.end || item.to === '/expenses'}
              onClick={() => setOpen(false)}
              sx={{ mx: 1, borderRadius: 2, '&.active': { bgcolor: 'action.selected', fontWeight: 600 } }}
            >
              <ListItemIcon sx={{ minWidth: 36 }}>{item.icon}</ListItemIcon>
              <ListItemText primary={item.label} />
            </ListItemButton>
          ),
        )}
      </List>
    </Box>
  );

  const doLogout = async () => {
    setAnchor(null);
    await dispatch(logout());
    navigate('/login');
  };

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <AppBar
        position="fixed"
        color="inherit"
        elevation={0}
        sx={{ zIndex: (t) => t.zIndex.drawer + 1, borderBottom: '1px solid #e3e6ee' }}
      >
        <Toolbar>
          {!desktop && (
            <IconButton edge="start" onClick={() => setOpen(true)} aria-label="Open menu">
              <MenuIcon />
            </IconButton>
          )}
          <Box sx={{ flexGrow: 1 }} />
          <Chip
            size="small"
            label={user?.role}
            color={user?.role === 'ADMIN' ? 'secondary' : 'default'}
            sx={{ mr: 1 }}
          />
          <IconButton onClick={(e) => setAnchor(e.currentTarget)} aria-label="Account menu">
            <Avatar sx={{ width: 32, height: 32 }}>{user?.full_name?.[0] || '?'}</Avatar>
          </IconButton>
          <Menu anchorEl={anchor} open={!!anchor} onClose={() => setAnchor(null)}>
            <MenuItem disabled>{user?.email}</MenuItem>
            <MenuItem
              onClick={() => {
                setAnchor(null);
                navigate('/profile');
              }}
            >
              Profile
            </MenuItem>
            <MenuItem onClick={doLogout} data-cy="logout">
              Log out
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>
      <Drawer
        variant={desktop ? 'permanent' : 'temporary'}
        open={desktop || open}
        onClose={() => setOpen(false)}
        sx={{ width: WIDTH, flexShrink: 0, '& .MuiDrawer-paper': { width: WIDTH, boxSizing: 'border-box' } }}
      >
        {drawer}
      </Drawer>
      <Box component="main" sx={{ flexGrow: 1, p: { xs: 2, md: 3 }, mt: 8, minWidth: 0 }}>
        <Outlet />
      </Box>
    </Box>
  );
}
