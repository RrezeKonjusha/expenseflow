/**
 * Screenshots of every page, desktop (1440x900) and mobile (390x844), into docs/screenshots/.
 * Needs the stack running and seeded (seed_demo --reset).
 *   cd tests/browser && node page-shots.mjs
 */
import fs from 'node:fs';
import puppeteer from 'puppeteer-core';

const BASE = process.env.BASE_URL || 'https://localhost';
const OUT = process.env.OUT_DIR || '../../docs/screenshots';
const chrome = process.env.CHROME_PATH || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const PASSWORD = 'Demo-Pass-2026!';
const DESKTOP = { width: 1440, height: 900 };
const MOBILE = { width: 390, height: 844, isMobile: true, hasTouch: true, deviceScaleFactor: 2 };
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

fs.mkdirSync(`${OUT}/desktop`, { recursive: true });
fs.mkdirSync(`${OUT}/mobile`, { recursive: true });
const browser = await puppeteer.launch({ executablePath: chrome, headless: true, acceptInsecureCerts: true });

async function session(email, viewport) {
  const context = await browser.createBrowserContext();
  const page = await context.newPage();
  await page.setViewport(viewport);
  await page.goto(`${BASE}/login`, { waitUntil: 'networkidle0' });
  let access = null;
  if (email) {
    access = await page.evaluate(
      (e, p) =>
        fetch('/api/v1/auth/login/', {
          method: 'POST',
          credentials: 'include',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email: e, password: p }),
        })
          .then((r) => r.json())
          .then((d) => d.access),
      email,
      PASSWORD,
    );
  }
  const api = (path) =>
    page.evaluate(
      (p, t) => fetch(p, { headers: { Authorization: `Bearer ${t}` } }).then((r) => r.json()),
      path,
      access,
    );
  return { page, context, api };
}

async function shot(page, path, name, dir, waitText) {
  await page.goto(BASE + path, { waitUntil: 'networkidle0' });
  if (waitText)
    await page.waitForFunction((t) => document.body.innerText.includes(t), { timeout: 15000 }, waitText);
  await sleep(700);
  await page.screenshot({ path: `${OUT}/${dir}/${name}.png` });
  console.log(`${dir}/${name}`);
}

// ---- desktop -------------------------------------------------------------------------------------------
let s = await session(null, DESKTOP);
await shot(s.page, '/login', '01-login', 'desktop', 'Sign in');
await shot(s.page, '/register', '02-register', 'desktop', 'Create');
await shot(s.page, '/forgot-password', '03-forgot-password', 'desktop', 'password');
await shot(s.page, '/activate/xx/invalid-token', '04-activate-invalid-link', 'desktop');
await shot(s.page, '/reset-password/xx/invalid-token', '05-reset-password', 'desktop', 'password');
await s.context.close();

s = await session('arta@expenseflow.dev', DESKTOP);
const mine = await s.api('/api/v1/expenses/?ordering=-created_at&page_size=100');
// the seed leaves Arta no drafts, so create one through the API (local stack only)
const projects = await s.api('/api/v1/projects/');
const alpha = (projects.results || projects).find((p) => p.code === 'ALPHA');
const draft = await s.page.evaluate(
  (body) =>
    fetch('/api/v1/auth/refresh/', { method: 'POST', credentials: 'include' })
      .then((r) => r.json())
      .then((d) =>
        fetch('/api/v1/expenses/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${d.access}` },
          body: JSON.stringify(body),
        }),
      )
      .then((r) => r.json()),
  {
    type: 'MEAL',
    project: alpha.id,
    amount: '48.00',
    attendees: 2,
    expense_date: new Date(Date.now() - 2 * 864e5).toISOString().slice(0, 10),
    description: 'Lunch with the Prishtina client team',
  },
);
if (!draft.id) throw new Error(`could not create a draft: ${JSON.stringify(draft)}`);
const rejected = mine.results.find((e) => e.status === 'REJECTED');
await shot(s.page, '/', '06-dashboard-employee', 'desktop', 'Waiting for approval');
await shot(s.page, '/expenses', '07-expense-list', 'desktop', 'Expenses');
await shot(s.page, '/expenses/new', '08-expense-form', 'desktop', 'New expense');
await shot(s.page, `/expenses/${draft.id}`, '09-expense-detail-draft', 'desktop', 'Timeline');
await shot(s.page, `/expenses/${draft.id}/edit`, '10-expense-edit', 'desktop', 'expense');
if (rejected)
  await shot(s.page, `/expenses/${rejected.id}`, '11-expense-detail-rejected', 'desktop', 'Rejected');
await shot(s.page, '/expenses/import', '12-import', 'desktop', 'Import');
await shot(s.page, '/profile', '13-profile', 'desktop', 'Profile');
await shot(s.page, '/no-such-page', '14-not-found', 'desktop');
await s.context.close();

s = await session('besa@expenseflow.dev', DESKTOP);
await shot(s.page, '/', '15-dashboard-manager', 'desktop', 'Approvals');
await shot(s.page, '/approvals', '16-approvals', 'desktop', 'Approve');
await s.context.close();

s = await session('admin@expenseflow.dev', DESKTOP);
const reports = await s.api('/api/v1/reports/');
const report = (reports.results || reports)[0];
await shot(s.page, '/', '17-dashboard-admin', 'desktop', 'Waiting for approval');
await s.page.goto(`${BASE}/reports`, { waitUntil: 'networkidle0' });
await s.page.click('[data-cy=run-report]');
await s.page.waitForFunction(() => document.body.innerText.includes('Total'), { timeout: 15000 });
await sleep(900);
await s.page.screenshot({ path: `${OUT}/desktop/18-report-builder.png` });
console.log('desktop/18-report-builder');
await shot(s.page, `/reports/${report.id}`, '19-saved-report', 'desktop', 'XLSX');
await shot(s.page, '/admin/users', '20-admin-users', 'desktop', 'arta@expenseflow.dev');
await shot(s.page, '/admin/departments', '21-admin-departments', 'desktop', 'Engineering');
await shot(s.page, '/admin/projects', '22-admin-projects', 'desktop', 'GAMMA');
await shot(s.page, '/admin/audit', '23-admin-audit', 'desktop', 'LOGIN');
await s.context.close();

// ---- mobile ---------------------------------------------------------------------------------------------
s = await session(null, MOBILE);
await shot(s.page, '/login', '01-login', 'mobile', 'Sign in');
await s.context.close();
s = await session('arta@expenseflow.dev', MOBILE);
await shot(s.page, '/', '02-dashboard', 'mobile', 'Waiting for approval');
await shot(s.page, '/expenses', '03-expense-list', 'mobile', 'Expenses');
await shot(s.page, '/expenses/new', '04-expense-form', 'mobile', 'New expense');
await s.page.goto(`${BASE}/`, { waitUntil: 'networkidle0' });
await s.page.click('[aria-label="Open menu"]');
await sleep(700);
await s.page.screenshot({ path: `${OUT}/mobile/05-menu-open.png` });
console.log('mobile/05-menu-open');
await s.context.close();

await browser.close();
