// Uses the pinned Anime2.5DRig ag-psd distribution; no canvas dependency.
const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'..');
const ag=require(path.join(root,'web/rig/lib/ag-psd.min.js'));
ag.initializeCanvas(()=>{throw new Error('Canvas rendering is not used');},
  (w,h)=>({width:w,height:h,data:new Uint8ClampedArray(w*h*4)}));
const native=process.argv.includes('--native');
const m=JSON.parse(fs.readFileSync(path.join(root,native?'work/native-layers/manifest.json':'work/layers/manifest.json')));
const imageData=(f,w,h)=>({width:w,height:h,data:new Uint8ClampedArray(fs.readFileSync(f))});
const psd={width:m.width,height:m.height,imageData:imageData(m.composite,m.width,m.height),
  children:m.children.map(c=>({name:c.name,left:c.left,top:c.top,
    imageData:imageData(c.raw,c.width,c.height)}))};
const psdPath=path.join(root,native?'assets/miku-native.psd':'assets/miku-lite.psd');
fs.writeFileSync(psdPath,ag.writePsdBuffer(psd,{generateThumbnail:false}));
if(native)fs.copyFileSync(psdPath,path.join(root,'web/rig/miku-native.psd'));
const parsed=ag.readPsd(fs.readFileSync(psdPath),{useImageData:true});
const rig=require(path.join(root,'web/rig/lib/rigger.js')).buildRig(parsed);
fs.writeFileSync(path.join(root,native?'docs/native-rig-validation.json':'docs/rig-validation.json'),JSON.stringify({layers:rig.layers.map(l=>
  ({name:l.name,group:l.group,physics:l.phys||null,width:l.w,height:l.h})),anchors:rig.anchors,
  warnings:rig.warnings,synth:rig.synth},null,2)+'\n');
console.log(`PSD built; ${rig.layers.length} render parts; ${rig.warnings.length} diagnostics.`);
