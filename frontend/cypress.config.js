import { defineConfig } from 'cypress';

export default defineConfig({
  e2e: {
    baseUrl: process.env.CYPRESS_BASE_URL || 'https://localhost',
    video: true,
    viewportWidth: 1366,
    viewportHeight: 860,
    env: { mailpitUrl: process.env.CYPRESS_MAILPIT_URL || 'http://localhost:8025' },
  },
});
