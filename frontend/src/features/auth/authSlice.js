import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import { authApi } from '../../api/endpoints';
import { refreshSession } from '../../api/client';

// The access token lives only in memory (Redux). On reload we ask /auth/refresh/,
// which reads the httpOnly refresh cookie, so no token is ever stored in localStorage.
export const bootstrap = createAsyncThunk('auth/bootstrap', async (_, { rejectWithValue }) => {
  try {
    await refreshSession();
    return true;
  } catch {
    return rejectWithValue(null);
  }
});

export const login = createAsyncThunk('auth/login', async (credentials) => authApi.login(credentials));

export const logout = createAsyncThunk('auth/logout', async () => {
  try {
    await authApi.logout();
  } catch {
    /* already logged out on the server */
  }
});

const initialState = { user: null, access: null, status: 'checking' };

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    sessionRefreshed(state, { payload }) {
      state.access = payload.access;
      state.user = payload.user;
      state.status = 'authenticated';
    },
    loggedOut() {
      return { ...initialState, status: 'anonymous' };
    },
    profileUpdated(state, { payload }) {
      state.user = { ...state.user, ...payload };
    },
  },
  extraReducers: (b) => {
    b.addCase(bootstrap.rejected, (state) => {
      state.status = 'anonymous';
    });
    b.addCase(login.fulfilled, (state, { payload }) => {
      state.access = payload.access;
      state.user = payload.user;
      state.status = 'authenticated';
    });
    b.addCase(logout.fulfilled, () => ({ ...initialState, status: 'anonymous' }));
  },
});

export const { sessionRefreshed, loggedOut, profileUpdated } = authSlice.actions;
export default authSlice.reducer;

export const selectUser = (s) => s.auth.user;
export const selectStatus = (s) => s.auth.status;
export const hasRole = (user, ...roles) => !!user && roles.includes(user.role);
