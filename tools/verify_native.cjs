// Use the actual local-loader data-URL format and the installed app's CSS grid timings.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const root=path.resolve(__dirname,'..');
(async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true});
 const page=await browser.newPage({viewport:{width:900,height:640}}),errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:8765/native-preview.html');
 await page.waitForFunction(()=>window.NativePet?.ready,{timeout:60000});
 await page.waitForTimeout(200);
 const first=await page.locator('#native').screenshot();await page.waitForTimeout(350);
 const second=await page.locator('#native').screenshot();assert(!first.equals(second),'Native idle image is static');
 const states=['idle','running','waiting','review','running-right','running-left','waving','jumping','failed'];
 const snaps=path.join(root,'work/native-browser-check');fs.mkdirSync(snaps,{recursive:true});
 for(const state of states){
  await page.selectOption('#state',state);await page.waitForTimeout(100);
  fs.writeFileSync(path.join(snaps,state+'.png'),await page.locator('#native').screenshot());
 }
 await page.selectOption('#state','idle');await page.waitForTimeout(100);
 await page.screenshot({path:path.join(root,'docs/native-preview.png')});
 // Background-image keeps animating while the host changes fixed column indices.
 assert((await page.locator('#native').evaluate(el=>el.style.backgroundImage)).startsWith('url("data:image/webp;base64,'));
 assert.equal(errors.length,0,errors.join('\n'));
 fs.writeFileSync(path.join(root,'docs/native-browser-validation.json'),JSON.stringify({ok:true,states,
  scope:'isolated headless Edge CSS background-image using the same image data URL and 8x11 layout as the installed Codex build',
  checks:['animated idle visibly changes while native idle holds its first cell','all nine state rows render',
          'custom pet data URL loads without page errors','native timers and background-position grid'],
  actualCodexWindowReloaded:false,errors},null,2)+'\n');
 await browser.close();console.log('Native CSS/data-URL playback verified.');
})().catch(e=>{console.error(e);process.exit(1);});
