// Uses the pinned Anime2.5DRig ag-psd distribution; no canvas dependency.
const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'..');
const ag=require(path.join(root,'web/rig/lib/ag-psd.min.js'));
ag.initializeCanvas(()=>{throw new Error('Canvas rendering is not used');},
  (w,h)=>({width:w,height:h,data:new Uint8ClampedArray(w*h*4)}));
const m=JSON.parse(fs.readFileSync(path.join(root,'work/layers/manifest.json')));
const imageData=(f,w,h)=>({width:w,height:h,data:new Uint8ClampedArray(fs.readFileSync(f))});
const psd={width:m.width,height:m.height,imageData:imageData(m.composite,m.width,m.height),
  children:m.children.map(c=>({name:c.name,left:c.left,top:c.top,
    imageData:imageData(c.raw,c.width,c.height)}))};
fs.writeFileSync(path.join(root,'assets/miku-lite.psd'),ag.writePsdBuffer(psd,{generateThumbnail:false}));
const parsed=ag.readPsd(fs.readFileSync(path.join(root,'assets/miku-lite.psd')),{useImageData:true});
const rig=require(path.join(root,'web/rig/lib/rigger.js')).buildRig(parsed);
fs.writeFileSync(path.join(root,'docs/rig-validation.json'),JSON.stringify({layers:rig.layers.map(l=>
  ({name:l.name,group:l.group,physics:l.phys||null,width:l.w,height:l.h})),anchors:rig.anchors,
  warnings:rig.warnings,synth:rig.synth},null,2)+'\n');
console.log(`PSD built; ${rig.layers.length} render parts; ${rig.warnings.length} diagnostics.`);
