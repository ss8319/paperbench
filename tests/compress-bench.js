// Compression benchmark: every PDF in tests/pdfs through every compression level.
// Usage: node tests/compress-bench.js [--offline]
const fs = require('fs'), path = require('path');
const { openApp, save, ROOT } = require('./common');
const MODES = ['none', 'light', 'med', 'strong', 'flat'];
(async () => {
  const dir = path.join(ROOT, 'tests/pdfs'), out = path.join(ROOT, 'tests/out');
  fs.mkdirSync(out, { recursive: true });
  const files = fs.readdirSync(dir).filter(f => f.endsWith('.pdf')).sort();
  if (!files.length) throw new Error('No PDFs in tests/pdfs. Run python3 tests/make_test_pdfs.py tests/pdfs first.');
  console.log('file'.padEnd(18) + 'original'.padStart(10) + MODES.map(m => m.padStart(10)).join(''));
  for (const f of files) {
    const { browser, page } = await openApp({ offline: process.argv.includes('--offline') });
    await page.setInputFiles('#fileIn', path.join(dir, f));
    await page.waitForFunction(() => !/example/.test(document.querySelector('.card .from').textContent));
    const row = [f.replace('.pdf', '').padEnd(18), (fs.statSync(path.join(dir, f)).size / 1024 | 0).toString().padStart(9) + 'K'];
    for (const m of MODES) {
      await page.selectOption('#comp', m);
      await page.fill('#outName', `${f.replace('.pdf', '')}-${m}.pdf`);
      row.push(((await save(page, path.join(out, `${f.replace('.pdf', '')}-${m}.pdf`))) / 1024 | 0).toString().padStart(9) + 'K');
    }
    console.log(row.join(''));
    await browser.close();
  }
})().catch(e => { console.error(e); process.exit(1); });
