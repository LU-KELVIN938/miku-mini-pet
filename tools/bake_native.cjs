// Offline mesh rendering only, in an isolated headless browser.
const fs=require('node:fs'),path=require('node:path');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const root=path.resolve(__dirname,'..');
(async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true,args:['--enable-unsafe-swiftshader']});
 const page=await browser.newPage();
 await page.goto('http://127.0.0.1:8765/rig/index.html?obs=1&model=miku-native.psd&settings=lite-settings.json');
 await page.waitForFunction(()=>window.MikuPetRig?.ready,{timeout:45000});
 await page.evaluate(()=>window.MikuPetRig.setPaused(true));
 const poses={idle:{angleX:0,angleY:0,angleZ:0,body:0},running:{angleX:.08,angleY:-.12,angleZ:.08,body:.08},
 waiting:{angleX:-.10,angleY:.10,angleZ:-.12,body:0},review:{angleX:.10,angleY:-.10,angleZ:.10,body:.03}};
 for(const [state,base] of Object.entries(poses)){
  const dest=path.join(root,'work/native-bake',state);fs.mkdirSync(dest,{recursive:true});
  for(let i=0;i<32;i++){
   const phase=i/32*Math.PI*2,blink=i===22?0:i===21||i===23?.35:i===20||i===24?.8:1;
   const pose={...base,angleX:base.angleX+.06*Math.sin(phase),angleZ:base.angleZ+.04*Math.sin(phase),
     body:base.body+.04*Math.sin(phase),eyeOpenL:blink,eyeOpenR:blink,
     breath:.5+.5*Math.sin(phase),breathHead:.5+.5*Math.sin(phase-.6)};
   const data=await page.evaluate(({pose,phase})=>window.MikuPetRig.captureNative(pose,phase),{pose,phase});
   fs.writeFileSync(path.join(dest,String(i).padStart(2,'0')+'.png'),Buffer.from(data.split(',')[1],'base64'));
  }
 }
 await browser.close();console.log('Baked 32 transparent frames for each of four native states.');
})().catch(e=>{console.error(e);process.exit(1);});
