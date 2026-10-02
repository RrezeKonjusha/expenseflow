/** Prints the documentation HTML to an A4 PDF with page numbers. usage: node print-pdf.mjs in.html out.pdf */
import path from 'node:path';
import puppeteer from 'puppeteer-core';

const [input, output] = process.argv.slice(2);
const chrome =
  process.env.CHROME_PATH ||
  (process.platform === 'darwin' ? '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' : '/usr/bin/google-chrome');
const browser = await puppeteer.launch({ executablePath: chrome, headless: true });
const page = await browser.newPage();
await page.goto(`file://${path.resolve(input)}`, { waitUntil: 'load' });
await page.pdf({
  path: output,
  format: 'A4',
  printBackground: true,
  preferCSSPageSize: true,
  displayHeaderFooter: true,
  headerTemplate: '<span></span>',
  footerTemplate:
    '<div style="width:100%;font-size:8pt;color:#6a7179;padding:0 18mm;display:flex;justify-content:space-between;font-family:Arial">' +
    '<span>ExpenseFlow · Rreze Konjusha</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>',
});
await browser.close();
console.log(`wrote ${output}`);
