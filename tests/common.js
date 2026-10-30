// Shared test setup: opens index.html in headless Chromium, serving the CDN libraries from node_modules.
const { chromium } = require('playwright-core');
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
const LIB = {
  'pdf-lib.min.js': 'node_modules/pdf-lib/dist/pdf-lib.min.js',
  'pdf.min.js': 'node_modules/pdfjs-dist/build/pdf.min.js',
  'pdf.worker.min.js': 'node_modules/pdfjs-dist/build/pdf.worker.min.js',
};
async function openApp({ offline = false } = {}) {
  // Set CHROME to your Chrome/Chromium binary if Playwright can't find one.
  const opts = { args: ['--headless=new'] };
  if (process.env.CHROME) opts.executablePath = process.env.CHROME; else opts.channel = 'chrome';
  const browser = await chromium.launch(opts);
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 }, acceptDownloads: true });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.route('**/*', r => {
    const u = r.request().url();
    if (u.startsWith('file://')) return r.continue();
    const k = Object.keys(LIB).find(k => u.endsWith('/' + k));
    if (k) return r.fulfill({ body: fs.readFileSync(path.join(ROOT, LIB[k])), contentType: 'application/javascript' });
    return r.abort();
  });
  const file = offline ? 'dist/paperbench-offline.html' : 'index.html';
  await page.goto('file://' + path.join(ROOT, file));
  await page.waitForFunction(() => document.querySelectorAll('.card').length > 0, null, { timeout: 15000 });
  return { browser, page, errors };
}
async function save(page, outPath) {
  const [dl] = await Promise.all([page.waitForEvent('download', { timeout: 180000 }), page.click('#saveBtn')]);
  await dl.saveAs(outPath);
  return fs.statSync(outPath).size;
}
module.exports = { openApp, save, ROOT };
