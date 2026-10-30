// End-to-end test: clicks through page operations, every edit tool and every save mode.
// Usage: node tests/e2e.js [--offline]
// Needs tests/pdfs/{scan,paper,cmyk}.pdf from: python3 tests/make_test_pdfs_basic.py tests/pdfs
const fs = require('fs'), path = require('path'), assert = require('assert');
const { openApp, save, ROOT } = require('./common');

(async () => {
  const offline = process.argv.includes('--offline');
  const { browser, page, errors } = await openApp({ offline });
  const out = path.join(ROOT, 'tests/out'); fs.mkdirSync(out, { recursive: true });
  const cards = () => page.locator('.card');
  const step = (name) => console.log('✓', name);

  assert.strictEqual(await cards().count(), 3); step('example file loads');

  await page.setInputFiles('#fileIn', ['scan.pdf', 'paper.pdf', 'cmyk.pdf'].map(f => path.join(ROOT, 'tests/pdfs', f)));
  await page.waitForFunction(() => document.querySelectorAll('.card').length === 8, null, { timeout: 30000 });
  step('opens and merges 3 files (8 pages)');

  await cards().nth(4).locator('[data-act=rotr]').click();
  await cards().nth(7).locator('[data-act=mvl]').click();
  await cards().nth(3).locator('[data-act=del]').click();
  assert.strictEqual(await cards().count(), 7);
  await page.keyboard.press('Control+z');
  assert.strictEqual(await cards().count(), 8); step('rotate, move, delete, undo');
  await cards().nth(3).locator('[data-act=del]').click();
  await cards().nth(0).dragTo(cards().nth(2), { targetPosition: { x: 140, y: 60 } });
  assert.deepStrictEqual((await page.$$eval('.card .from', e => e.map(x => x.textContent))).slice(0, 3), ['scan · p2', 'scan · p3', 'scan · p1']);
  step('drag to reorder');

  await cards().nth(0).locator('.paper').click();
  await page.waitForTimeout(1500);
  const bb = await page.locator('#ov').boundingBox();
  await page.click('[data-tool=text]');
  await page.mouse.click(bb.x + 80, bb.y + 60);
  await page.keyboard.type('Hello'); await page.keyboard.press('Enter');
  await page.click('[data-tool=draw]');
  await page.mouse.move(bb.x + 100, bb.y + 200); await page.mouse.down();
  for (let i = 0; i < 20; i++) await page.mouse.move(bb.x + 100 + i * 10, bb.y + 200 + Math.sin(i) * 20);
  await page.mouse.up();
  for (const [tool, y] of [['hl', 300], ['wo', 400]]) {
    await page.click(`[data-tool=${tool}]`);
    await page.mouse.move(bb.x + 60, bb.y + y); await page.mouse.down();
    await page.mouse.move(bb.x + 300, bb.y + y + 35, { steps: 5 }); await page.mouse.up();
  }
  await page.click('[data-tool=sig]');
  const sp = await page.locator('#sigpad').boundingBox();
  await page.mouse.move(sp.x + 40, sp.y + 120); await page.mouse.down();
  for (let i = 0; i < 30; i++) await page.mouse.move(sp.x + 40 + i * 12, sp.y + 90 + Math.sin(i / 2) * 40);
  await page.mouse.up();
  await page.click('#sigUse');
  await page.mouse.click(bb.x + 300, bb.y + 550);
  await page.mouse.move(bb.x + 300, bb.y + 550); await page.mouse.down();
  await page.mouse.move(bb.x + 350, bb.y + 600, { steps: 5 }); await page.mouse.up();
  await page.click('#bigger');
  await page.click('[data-tool=text]');
  await page.mouse.click(bb.x + 85, bb.y + 55);
  assert.strictEqual(await page.inputValue('#txt'), 'Hello');
  await page.keyboard.press('End'); await page.keyboard.type('!'); await page.keyboard.press('Enter');
  step('text, draw, highlight, whiteout, signature, move, resize, re-edit text');

  await page.click('#tabPages'); await page.waitForTimeout(500);
  const sizes = {};
  for (const mode of ['none', 'light', 'med', 'strong', 'flat']) {
    await page.selectOption('#comp', mode);
    await page.fill('#outName', `e2e-${mode}.pdf`);
    sizes[mode] = await save(page, path.join(out, `e2e-${mode}.pdf`));
  }
  assert.ok(sizes.med < sizes.none * 0.3, 'Balanced compression should cut this set by >70%');
  assert.ok(sizes.strong <= sizes.med && sizes.med <= sizes.light);
  step('save in all 5 modes: ' + Object.entries(sizes).map(([k, v]) => `${k} ${(v / 1048576).toFixed(1)}MB`).join(', '));

  await cards().nth(1).locator('[data-act=pick]').check();
  await page.check('#scopeSel'); await page.selectOption('#comp', 'none');
  await save(page, path.join(out, 'e2e-selected.pdf')); step('save selected pages only');

  await page.setViewportSize({ width: 390, height: 800 }); await page.waitForTimeout(500);
  assert.ok(await page.evaluate(() => document.documentElement.scrollWidth) <= 390, 'no horizontal scroll on phones');
  step('phone layout');

  assert.deepStrictEqual(errors, []); step('no page errors');
  await browser.close();
})().catch(e => { console.error('✗', e.message); process.exit(1); });
