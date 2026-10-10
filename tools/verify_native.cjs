// Validate the final release asset in an isolated headless CSS/data-URL renderer.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {createHash}=require('node:crypto');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const root=path.resolve(__dirname,'..');
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
(async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true});
 try{
  const page=await browser.newPage({viewport:{width:1000,height:720}}),errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  await page.goto('http://127.0.0.1:8766/native-preview.html?manual=1');
  await page.waitForFunction(()=>window.NativePet?.ready);
  const set=(state,opts={})=>page.evaluate(({state,opts})=>window.NativePet.setState(state,opts),{state,opts});
  const advance=ms=>page.evaluate(ms=>window.NativePet.advance(ms),ms);
  const frame=()=>page.evaluate(()=>window.NativePet.getFrame());
  const shot=async()=>hash(await page.locator('#native').screenshot());
  const config=JSON.parse(fs.readFileSync(path.join(root,'web/animations.json'),'utf8'));
  const results={};
  for(const row of config.states){
   await set(row.state,{loop:true});const cells=[];
   for(let column=0;column<row.count;column++){
    const f=await frame();assert.equal(f.row,row.row);assert.equal(f.column,column);
    cells.push(await shot());await advance(row.durations[column]*(row.state==='idle'?6:1));
   }
   assert.equal((await frame()).column,0);assert.equal(await shot(),cells[0]);
   if(['running-right','running-left'].includes(row.state))assert.equal(new Set(cells).size,8);
   results[row.state]={distinctRenderedCells:new Set(cells).size,loopMs:row.durations.reduce((a,b)=>a+b,0)*(row.state==='idle'?6:1)};
  }
  await set('running-right');await advance(3179);assert.equal((await frame()).row,1);
  await advance(1);assert.equal((await frame()).row,0);
  await set('running-right');await advance(250);await set('idle');await advance(500);assert.equal((await frame()).row,0);
  await set('running-right');await advance(250);await set('running-left');assert.equal((await frame()).column,0);assert.equal((await frame()).row,2);
  await set('running-right',{reducedMotion:true});const reduced=await shot();await advance(4000);assert.equal(await shot(),reduced);
  for(let direction=0;direction<16;direction++){
   await page.evaluate(d=>window.NativePet.setLookFrame(9+Math.floor(d/8),d%8),direction);
   const still=await shot();await page.waitForTimeout(20);assert.equal(await shot(),still);
  }
  await set('running-right',{lookFrame:{row:9,column:4}});assert.equal((await frame()).row,1);
  const frozen=await shot();await page.waitForTimeout(400);assert.equal(await shot(),frozen,'Unexpected independent image clock');
  assert((await page.locator('#native').evaluate(el=>el.style.backgroundImage)).startsWith('url("data:image/webp;base64,'));
  assert.equal(errors.length,0,errors.join('\n'));
  await page.screenshot({path:path.join(root,'docs/native-preview.png')});
  const bytes=fs.readFileSync(path.join(root,'assets/spritesheet.webp'));
  const report={ok:true,scope:'isolated headless Edge CSS/data-URL rendering of the final static v2 atlas; preview model of the installed native timers',
   atlasSha256:hash(bytes),states:results,checks:['all nine rows','eight distinct movement poses','1060ms movement loop',
    'no independent image clock','short stop','rapid reversal','three-cycle fallback','reduced motion','16 static look poses'],
   actualCodexWindowVerified:false,actualCodexWindowReloaded:false,errors};
  fs.writeFileSync(path.join(root,'docs/native-browser-validation.json'),JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify({ok:true,movement:results['running-right'],actualCodexWindowVerified:false}));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
