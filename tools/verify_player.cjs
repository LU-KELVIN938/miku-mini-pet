// Integration checks using an isolated headless browser, never the user's browser profile.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const root=path.resolve(__dirname,'..');
(async()=>{
  const browser=await chromium.launch({channel:'msedge',headless:true,args:['--enable-unsafe-swiftshader']});
  const page=await browser.newPage({viewport:{width:1000,height:800}}),errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  await page.goto('http://127.0.0.1:8765/',{waitUntil:'networkidle'});
  await page.waitForFunction(()=>window.MikuMini?.state().rigReady,{timeout:45000});
  await page.waitForTimeout(1400);
  const frames=await page.frames().find(f=>f.url().includes('/rig/index.html'));
  const rig=await frames.evaluate(()=>window.MikuPetRig.snapshot());
  assert(rig.layers>=6);assert.equal(rig.auto.cam,false);assert.equal(rig.auto.mic,false);
  assert.equal(rig.auto.mouse,false);assert.equal(rig.auto.talk,false);
  assert.equal(await frames.evaluate(()=>document.querySelector('meta[name="color-scheme"]').content),'light');
  const results=[];
  for(const state of ['idle','running','waiting','review','running-right','running-left','waving','jumping','failed']){
    await page.selectOption('#state',state);await page.waitForTimeout(500);
    const snapshot=await page.evaluate(()=>window.MikuMini.state());
    assert.equal(snapshot.state,state);
    assert.equal(snapshot.activeLayered,['idle','running','waiting','review'].includes(state));
    if(['running-right','running-left','waving','jumping'].includes(state))assert.equal(snapshot.outputFrames,snapshot.sourceFrames*2);
    results.push(snapshot);
  }
  await page.selectOption('#state','idle');await page.selectOption('#fps','60');
  await page.waitForTimeout(100);assert.equal((await frames.evaluate(()=>window.MikuPetRig.snapshot())).fps,60);
  await page.click('#pause');await page.waitForTimeout(100);
  assert.equal((await frames.evaluate(()=>window.MikuPetRig.snapshot())).paused,true);
  await page.click('#pause');await page.selectOption('#fps','30');
  await page.waitForTimeout(800);
  await page.screenshot({path:path.join(root,'docs/player-preview.png'),fullPage:true});
  await page.locator('#rig').screenshot({path:path.join(root,'docs/layered-preview.png')});
  await page.selectOption('#state','running-right');await page.waitForTimeout(300);
  await page.screenshot({path:path.join(root,'docs/interpolation-preview.png'),fullPage:true});
  // Registered mode must remain available even for a state with interpolated frames.
  await page.selectOption('#mode','registered');await page.waitForTimeout(100);
  assert.equal((await page.evaluate(()=>window.MikuMini.state())).outputFrames,8);
  await page.evaluate(()=>{window.MikuMini.receiveCodex({state:'waiting'});window.MikuMini.receiveCodex({state:'working'});});
  await page.waitForTimeout(350);assert.equal((await page.evaluate(()=>window.MikuMini.state())).state,'running');
  // Returning to the current state must cancel an obsolete queued transition.
  await page.evaluate(()=>{window.MikuMini.receiveCodex({state:'waiting'});window.MikuMini.receiveCodex({state:'working'});});
  await page.waitForTimeout(350);assert.equal((await page.evaluate(()=>window.MikuMini.state())).state,'running');
  await page.selectOption('#state','waving');await page.waitForTimeout(100);
  assert.equal((await frames.evaluate(()=>window.MikuPetRig.snapshot())).paused,true);
  await page.goto('http://127.0.0.1:8765/?desktop=1',{waitUntil:'networkidle'});
  await page.waitForFunction(()=>window.MikuMini?.state().rigReady,{timeout:45000});
  assert(await page.locator('body.desktop').count());
  assert.equal(await page.evaluate(()=>getComputedStyle(document.documentElement).backgroundColor),'rgba(0, 0, 0, 0)');
  assert.equal(await page.locator('.original').isVisible(),false);
  assert.equal(errors.length,0,errors.join('\n'));
  fs.writeFileSync(path.join(root,'docs/player-validation.json'),JSON.stringify({ok:true,
    tested:'isolated headless Microsoft Edge; not desktop-window performance',rig,states:results,
    checks:['all 9 states','hybrid rig/sprite selection','2x interpolation selection','30/60 target controls',
      'pause/resume','registered fallback','state debounce','desktop layout','no camera/microphone/global pointer input'],errors},null,2)+'\n');
  await browser.close();console.log('Player integration checks passed.');
})().catch(e=>{console.error(e);process.exit(1);});
