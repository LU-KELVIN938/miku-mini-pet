// Exercise the native CSS/data-URL path in an isolated headless browser.
// This never reads or controls the user's screen or installed Codex window.
const fs = require('node:fs'), path = require('node:path'), assert = require('node:assert/strict');
const {createHash} = require('node:crypto');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const root = path.resolve(__dirname, '..');
const hash = bytes => createHash('sha256').update(bytes).digest('hex');

(async () => {
  const browser = await chromium.launch({channel: 'msedge', headless: true});
  try {
    const page = await browser.newPage({viewport: {width: 950, height: 720}});
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    await page.goto('http://127.0.0.1:8766/gait-preview.html?manual=1');
    await page.waitForFunction(() => window.GaitPreview?.ready);
    const set = (state, options = {}) => page.evaluate(({state, options}) => window.GaitPreview.setState(state, options), {state, options});
    const advance = ms => page.evaluate(ms => window.GaitPreview.advance(ms), ms);
    const frame = () => page.evaluate(() => window.GaitPreview.getFrame());
    const currentPixels = async () => hash(await page.locator('#candidate').screenshot());
    const states = {};
    for (const [state, row] of [['running-right', 1], ['running-left', 2]]) {
      await set(state, {loop: true});
      const pictures = [];
      for (let column = 0; column < 8; column++) {
        const f = await frame();
        assert.equal(f.row, row); assert.equal(f.column, column);
        assert.equal(f.duration, column === 7 ? 220 : 120);
        pictures.push(await currentPixels());
        await advance(column === 7 ? 220 : 120);
      }
      assert.equal((await frame()).column, 0, 'Loop must return exactly to column zero');
      assert.equal(await currentPixels(), pictures[0], 'Loop seam must return to the same rendered first frame');
      assert.equal(new Set(pictures).size, 8, 'Native columns must display distinct poses');
      states[state] = {renderedDistinctCells: new Set(pictures).size, loopMs: 1060};
    }
    await set('running-right'); await advance(3179);
    assert.equal((await frame()).row, 1);
    await advance(1); assert.equal((await frame()).row, 0, 'Installed host contract falls back to idle after three cycles');
    await set('running-right'); await advance(250);
    await set('idle'); await advance(500);
    assert.equal((await frame()).row, 0, 'Short-drag release must cancel the old action timeline');
    await set('running-right'); await advance(250); await set('running-left');
    assert.deepEqual({row: (await frame()).row, column: (await frame()).column}, {row: 2, column: 0});
    await set('running-right', {reducedMotion: true}); await advance(4000);
    assert.equal((await frame()).column, 0);
    await set('idle', {lookFrame: {row: 9, column: 4}});
    assert.equal((await frame()).row, 9);
    await set('running-right', {lookFrame: {row: 9, column: 4}});
    assert.equal((await frame()).row, 1, 'Direction movement does not use the overlay look grid');
    const frozen = await currentPixels();
    await page.waitForTimeout(500);
    assert.equal(await currentPixels(), frozen, 'Image must not advance on an independent WebP clock');
    assert.equal(errors.length, 0, errors.join('\n'));
    assert((await page.locator('#candidate').evaluate(el => el.style.backgroundImage)).startsWith('url("data:image/webp;base64,'));
    await page.screenshot({path: path.join(root, 'work/gait-repair/browser-preview.png')});
    const report = {ok: true, scope: 'isolated headless CSS/data-URL rendering and preview model of the installed native timer contract',
      states, checks: ['distinct native columns', '1060ms cycle', 'pixel-stable image without a second clock',
        'three-cycle host fallback', 'short release', 'rapid reversal', 'reduced motion', 'directional look gating'],
      completeAlternatingGaitVerified: false, actualCodexWindowVerified: false, errors};
    fs.writeFileSync(path.join(root, 'work/gait-repair/browser-validation.json'), JSON.stringify(report, null, 2)+'\n');
    console.log(JSON.stringify(report));
  } finally {await browser.close();}
})().catch(error => {console.error(error); process.exitCode = 1;});
