/* Small adapter; continuous rigging and WebGL rendering are supplied by Anime2.5DRig. */
(async function(){
'use strict';
const $=id=>document.getElementById(id),config=await (await fetch('animations.json')).json();
const rows=new Map(config.states.map(r=>[r.state,r]));
const params=new URLSearchParams(location.search),desktop=params.has('desktop');
if(desktop){document.body.classList.add('desktop');document.documentElement.style.background='transparent';}
const original=await loadImage('source-spritesheet.webp'),images=new Map();
async function loadImage(src){const i=new Image();i.src=src;await i.decode();return i;}
await Promise.all([...config.states.flatMap(r=>r.frames),...Object.values(config.interpolation).flatMap(r=>r.frames)]
  .map(async src=>images.set(src,await loadImage(src))));
const oc=$('original').getContext('2d'),cc=$('optimized').getContext('2d');
const rigFrame=$('rig'),area=document.querySelector('.pet-area');
let state='idle',mode='hybrid',paused=false,fps=30,elapsed=0,last=performance.now(),lastDraw=0;
let activeLayered=false,lastTechnique='',rigReady=false,currentPose={},queuedPose={},switchAt=-Infinity;
const layerStates=new Set(['idle','running','waiting','review']);
const poses={idle:{angleX:0,angleY:0,angleZ:0,body:0},running:{angleX:.08,angleY:-.12,angleZ:.08,body:.08},
  waiting:{angleX:-.10,angleY:.10,angleZ:-.12,body:0},review:{angleX:.10,angleY:-.10,angleZ:.10,body:.03}};
function bridge(){return rigFrame.contentWindow.MikuPetRig;}
function setState(value){if(!rows.has(value))return;state=value;$('state').value=value;elapsed=0;switchAt=performance.now();queuedPose=poses[value]||poses.idle;}
function frameIndex(durations,time){const total=durations.reduce((a,b)=>a+b,0);let t=((time%total)+total)%total;
  for(let i=0;i<durations.length;i++){if(t<durations[i])return i;t-=durations[i];}return 0;}
function clear(ctx){ctx.clearRect(0,0,192,208);}
function drawSprite(ctx,sequence,time){clear(ctx);ctx.drawImage(images.get(sequence.frames[frameIndex(sequence.durations,time)]),0,0);}
function selectSequence(){const row=rows.get(state);return mode!=='registered'&&config.interpolation[state]||row;}
function updateRig(dt){const b=bridge();if(!b?.ready)return;rigReady=true;
  const visible=mode==='hybrid'&&layerStates.has(state)&&!document.hidden;
  b.setFPS(fps);b.setPaused(paused||!visible);
  if(paused||!visible)return;
  const target=queuedPose;const k=1-Math.exp(-dt*10);
  for(const key of ['angleX','angleY','angleZ','body'])currentPose[key]=(currentPose[key]||0)+((target[key]||0)-(currentPose[key]||0))*k;
  b.pose(currentPose);
}
function tick(now){requestAnimationFrame(tick);const dt=Math.min(.1,(now-last)/1000);last=now;
  if(!paused)elapsed+=dt*1000;updateRig(dt);
  if(now-lastDraw<1000/fps-.5)return;lastDraw=now;
  const row=rows.get(state),i=frameIndex(row.durations,elapsed);clear(oc);oc.drawImage(original,i*192,row.row*208,192,208,0,0,192,208);
  activeLayered=mode==='hybrid'&&layerStates.has(state)&&rigReady;
  area.classList.toggle('layered',activeLayered);
  const sequence=selectSequence();if(!activeLayered)drawSprite(cc,sequence,elapsed);
  const technique=activeLayered?'呼吸 · 眨眼 · 发梢轻摆':sequence!==row?'精选补帧 · 保留动作节奏':'保留原动作 · 位置微调';
  if(technique!==lastTechnique){lastTechnique=technique;$('technique').textContent=technique;}
  const label=$('state').selectedOptions[0].textContent;
  $('status').textContent=paused?'已暂停':`${label} · ${fps} 帧播放目标`;
}
$('state').addEventListener('change',e=>setState(e.target.value));
$('mode').addEventListener('change',e=>{mode=e.target.value;elapsed=0;});
$('fps').addEventListener('change',e=>{fps=Number(e.target.value);});
$('pause').addEventListener('click',()=>{paused=!paused;$('pause').textContent=paused?'继续':'暂停';$('pause').setAttribute('aria-pressed',String(paused));});
$('greet').addEventListener('click',()=>{setState('waving');setTimeout(()=>setState('idle'),1400);});
$('quit').addEventListener('click',()=>window.pywebview?.api.quit());
document.addEventListener('visibilitychange',()=>{last=performance.now();});
const codexMap={idle:'idle',running:'running',working:'running',thinking:'running',waiting:'waiting',needs_input:'waiting',
  review:'review',completed:'review',done:'review',failed:'failed',error:'failed',blocked:'waiting',paused:'waiting',interrupted:'failed'};
let pendingState=null,pendingTimer=null;
function receiveCodex(payload){const value=codexMap[payload?.state]||'idle';
  if(state===value){clearTimeout(pendingTimer);pendingState=null;return;}
  if(pendingState===value)return;pendingState=value;clearTimeout(pendingTimer);
  pendingTimer=setTimeout(()=>{setState(value);pendingState=null;},220);
}
window.MikuMini=Object.freeze({setState,receiveCodex,state:()=>({state,mode,paused,fps,rigReady,activeLayered,
  sourceFrames:rows.get(state).count,outputFrames:selectSequence().frames.length,loopMs:rows.get(state).durations.reduce((a,b)=>a+b,0)})});
queuedPose=poses.idle;requestAnimationFrame(tick);
})().catch(error=>{document.getElementById('status').textContent='加载失败：'+error.message;console.error(error);});
