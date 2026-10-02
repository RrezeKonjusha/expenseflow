/**
 * Regression test for #78: leaving pages while their /auth/refresh/ call is in flight must not sign the user out.
 * Runs in real Chrome without a proxy (Cypress rewrites cookies in its proxy, so it cannot test this reliably).
 *
 *   cd tests/browser && npm i --no-save puppeteer-core@24
 *   CHROME_PATH=/usr/bin/google-chrome BASE_URL=https://localhost node refresh-race.mjs
 */
import puppeteer from 'puppeteer-core';

const BASE = process.env.BASE_URL || 'https://localhost';
const RUNS = Number(process.env.RUNS || 5);
const chrome = process.env.CHROME_PATH || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';

async function run(browser) {
  const context = await browser.createBrowserContext(); // fresh cookies and storage per run
  try {
    const page = await context.newPage();
    await page.goto(`${BASE}/login`, { waitUntil: 'networkidle0' });
    const login = await page.evaluate(() =>
      fetch('/api/v1/auth/login/', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: 'arta@expenseflow.dev', password: 'Demo-Pass-2026!' }),
      }).then((r) => r.status),
    );
    if (login !== 200) throw new Error(`login returned ${login}`);
    // leave each page as soon as it has loaded, while its refresh call is still running
    for (const path of ['/', '/expenses', '/profile', '/', '/expenses']) {
      await page.goto(BASE + path, { waitUntil: 'load' });
    }
    await page.goto(`${BASE}/`, { waitUntil: 'load' });
    await page.waitForFunction(() => /Waiting for approval|Sign in/.test(document.body.innerText), {
      timeout: 10000,
    });
    return page.evaluate(() => document.body.innerText.includes('Waiting for approval'));
  } finally {
    await context.close();
  }
}

const browser = await puppeteer.launch({ executablePath: chrome, headless: true, acceptInsecureCerts: true });
let passed = 0;
for (let i = 1; i <= RUNS; i += 1) {
  const ok = await run(browser).catch((err) => {
    console.log(`run ${i}: error ${err.message}`);
    return false;
  });
  console.log(`run ${i}: ${ok ? 'still signed in' : 'SIGNED OUT'}`);
  if (ok) passed += 1;
}
await browser.close();
console.log(`${passed}/${RUNS} runs kept the session`);
process.exit(passed === RUNS ? 0 : 1);
