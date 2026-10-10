"""Apply a small same-origin player bridge to the pinned upstream editor."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'web/rig/lib/app.js';source=path.read_text('utf-8')
if 'MikuPetRig' not in source:
    source=source.replace("const OBS_MODE=QUERY.get('obs')==='1', CAMERA_MODE=QUERY.get('cam')==='1';",
      "const OBS_MODE=QUERY.get('obs')==='1', CAMERA_MODE=false;")
    source=source.replace("  auto.cam=true;\n  sync.listen();","  auto.cam=false;\n  sync.listen();")
    # The upstream model query intentionally requires a path inside its directory.
    source=source.replace("let last=performance.now(),simulationTime=last,fpsN=0,fpsT=last;",
      "let mikuFPS=30,mikuLastTick=0;\nlet last=performance.now(),simulationTime=last,fpsN=0,fpsT=last;")
    source=source.replace('  requestAnimationFrame(tick);\n  const dt=',
      '  requestAnimationFrame(tick);\n  if(now-mikuLastTick<1000/mikuFPS-.5)return; mikuLastTick=now;\n  const dt=')
    bridge="""
// Miku Mini integration: no device input, bounded pose values and frame rate.
Object.defineProperty(window,'MikuPetRig',{value:Object.freeze({
  get ready(){return layers.length>0;},
  pose(values){for(const key of ['angleX','angleY','angleZ','body']){
    if(Number.isFinite(values[key]))setSlider(key,clamp(values[key],-.18,.18));}},
  setFPS(value){mikuFPS=value===60?60:30;},
  setPaused(value){paused=!!value;},
  snapshot(){return {fps:mikuFPS,paused,layers:layers.length,params:{...T},auto:{...auto}};},
  captureForQA(now,dt){render(animate(now,dt));return cv.toDataURL('image/png');}
})});
"""
    source=source.replace('// ---------- start ----------',bridge+'\n// ---------- start ----------')
    path.write_text(source,encoding='utf-8')
    print('Patched existing rig renderer; camera and microphone remain disabled.')
index=ROOT/'web/rig/index.html'
index.write_text(index.read_text('utf-8').replace('name="color-scheme" content="dark"',
    'name="color-scheme" content="light"'),encoding='utf-8')
