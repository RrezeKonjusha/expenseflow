import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// In dev, Vite proxies the API so the SPA and API share one origin (needed for the refresh cookie).
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': { target: process.env.VITE_API_TARGET || 'http://localhost:8000', changeOrigin: true },
      '/health': { target: process.env.VITE_API_TARGET || 'http://localhost:8000', changeOrigin: true },
    },
  },
  build: {
    sourcemap: false,
    chunkSizeWarningLimit: 900,
    rollupOptions: {
      output: {
        manualChunks: {
          mui: ['@mui/material', '@mui/icons-material'],
          grid: ['@mui/x-data-grid'],
          charts: ['recharts'],
        },
      },
    },
  },
});
