/**
 * Screenshots every Storybook story into docs/screenshots/storybook/.
 *   cd frontend && npm run build-storybook && (cd storybook-static && python3 -m http.server 6007 &)
 *   cd tests/browser && node storybook-shots.mjs
 */
import fs from 'node:fs';
import puppeteer from 'puppeteer-core';

const BASE = process.env.STORYBOOK_URL || 'http://localhost:6007';
const OUT = process.env.OUT_DIR || '../../docs/screenshots/storybook';
const chrome = process.env.CHROME_PATH || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';

const index = await (await fetch(`${BASE}/index.json`)).json();
const stories = Object.values(index.entries).filter((e) => e.type === 'story');
fs.mkdirSync(OUT, { recursive: true });
const browser = await puppeteer.launch({
  executablePath: chrome,
  headless: true,
  defaultViewport: { width: 900, height: 520, deviceScaleFactor: 2 },
});
const page = await browser.newPage();
for (const s of stories) {
  await page.goto(`${BASE}/iframe.html?id=${s.id}&viewMode=story`, { waitUntil: 'networkidle0' });
  await page.waitForSelector('#storybook-root > *, .MuiDialog-root', { timeout: 10000 });
  await new Promise((r) => setTimeout(r, 400)); // let MUI transitions finish
  const path = `${OUT}/${s.id.replace('components-', '')}.png`;
  const dialog = await page.$('.MuiDialog-root');
  if (dialog)
    await page.screenshot({ path }); // dialogs: keep the backdrop
  else await (await page.$('#storybook-root')).screenshot({ path }); // others: crop to the component
  console.log('saved', s.id);
}
await browser.close();
