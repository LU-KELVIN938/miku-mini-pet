const fs=require('node:fs'),path=require('node:path');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
(async()=>{const b=await chromium.launch({channel:'msedge',headless:true,args:['--enable-unsafe-swiftshader']});
const p=await b.newPage();await p.goto('http://127.0.0.1:8765/');
await p.waitForFunction(()=>window.MikuMini?.state().rigReady);const f=p.frames().find(f=>f.url().includes('/rig/index.html'));
await f.evaluate(()=>window.MikuPetRig.setPaused(true));
const dest=path.resolve(__dirname,'../work/rig-captures');fs.mkdirSync(dest,{recursive:true});
for(let i=0;i<150;i++){const data=await f.evaluate(i=>window.MikuPetRig.captureForQA(10000+i*40,.04),i);
fs.writeFileSync(path.join(dest,String(i).padStart(3,'0')+'.png'),Buffer.from(data.split(',')[1],'base64'));}
await b.close();console.log('Captured six seconds of deterministic rig animation for visual review.');
})().catch(e=>{console.error(e);process.exit(1);});
