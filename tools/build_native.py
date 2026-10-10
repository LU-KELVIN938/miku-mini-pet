"""Build a self-contained animated v2 atlas plus a regular static fallback."""
from pathlib import Path
from hashlib import sha256
import json, sys
import numpy as np
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[1]
STATES=['idle','running-right','running-left','waving','jumping','failed','waiting','running','review']
COUNTS=[6,8,8,4,5,8,6,6,6]

def clear_hidden(im):
    a=np.array(im.convert('RGBA'));a[a[:,:,3]==0,:3]=0
    return Image.fromarray(a)

def build():
    source=Image.open(ROOT/'assets/source-spritesheet.webp').convert('RGBA')
    config=json.loads((ROOT/'web/animations.json').read_text('utf-8'))
    gestures={s:[Image.open(ROOT/'web'/p).convert('RGBA') for p in config['interpolation'][s]['frames']]
              for s in ['running-right','running-left','waving','jumping']}
    layered={s:[clear_hidden(Image.open(ROOT/f'work/native-bake/{s}/{i:02d}.png').resize((192,208),Image.Resampling.LANCZOS))
                for i in range(32)] for s in ['idle','waiting','running','review']}
    frames=[]
    for i in range(32):
        atlas=source.copy()
        for row,(s,n) in enumerate(zip(STATES,COUNTS)):
            if s in layered:cell=layered[s][i]
            elif s in gestures:
                seq=gestures[s];index=int((i%16)/16*len(seq)) if s=='jumping' else i%len(seq)
                cell=seq[index]
            else:continue
            for c in range(n):atlas.paste(cell,(c*192,row*208))
        frames.append(clear_hidden(atlas))
    animated=ROOT/'assets/spritesheet.webp'
    if '--reuse-encoded' not in sys.argv:
        frames[0].save(animated,save_all=True,append_images=frames[1:],duration=80,loop=0,
                       lossless=True,exact=True,method=4,minimize_size=False,kmin=9,kmax=17)
    fallback=source.copy()
    samples=[0,8,16,22,26,30]
    for row,(s,n) in enumerate(zip(STATES,COUNTS)):
        if s in layered:
            for c,i in enumerate(samples):fallback.paste(layered[s][i],(c*192,row*208))
    fallback.save(ROOT/'assets/static-spritesheet.webp',lossless=True,exact=True)
    checks=[]
    decoded=Image.open(animated)
    for i in range(decoded.n_frames):
        decoded.seek(i);a=np.array(decoded.convert('RGBA'));b=np.array(frames[i]);original=np.array(source)
        # The animation decoder may fill RGB under alpha=0; those values are invisible.
        a[a[:,:,3]==0,:3]=0
        assert np.array_equal(a,b),'WebP round-trip changed visible RGBA or alpha'
        assert np.array_equal(a[1872:],original[1872:]),'Look directions changed'
        assert np.array_equal(a[:208,1152:1344],original[:208,1152:1344]),'Static default changed'
        for r,n in enumerate([7,8,8,4,5,8,6,6,6,8,8]):
            assert not np.any(a[r*208:(r+1)*208,n*192:,3]),'Non-transparent unused cell'
    assert decoded.n_frames==32
    for row,s in enumerate(STATES):
        changed=any(not np.array_equal(np.array(im)[row*208:(row+1)*208],np.array(source)[row*208:(row+1)*208]) for im in frames)
        checks.append({'state':s,'visibleFramesChanged':changed,'source': 'baked original sprite layers' if s in layered else 'accepted RIFE frames' if s in gestures else 'original reaction'})
    assert all(x['visibleFramesChanged'] for x in checks if x['state']!='failed')
    # Small native-only previews, on a background that exposes alpha artifacts.
    dest=ROOT/'docs/native-previews';dest.mkdir(exist_ok=True)
    for s in ['idle','running','waiting','review','running-right','waving','jumping']:
        row=STATES.index(s);gif=[]
        for im in frames:
            cell=im.crop((0,row*208,192,(row+1)*208));bg=Image.new('RGBA',(192,208),(236,246,243,255));bg.alpha_composite(cell);gif.append(bg.convert('RGB'))
        gif[0].save(dest/f'{s}.gif',save_all=True,append_images=gif[1:],duration=80,loop=0)
    contact=Image.new('RGB',(900,640),'#ecf6f3');draw=ImageDraw.Draw(contact)
    for row,s in enumerate(['idle','running','waiting','review']):
        draw.text((8,row*156+60),s,fill='#31515b')
        for col,i in enumerate([0,8,16,22,26]):
            cell=layered[s][i].resize((132,143));contact.paste(cell,(100+col*155,row*156),cell)
    contact.save(ROOT/'docs/native-motion-sheet.png')
    shutil_source=ROOT/'web/native-spritesheet.webp'
    shutil_source.write_bytes(animated.read_bytes())
    report={'ok':True,'size':[1536,2288],'grid':[8,11],'cell':[192,208],'spriteVersionNumber':2,
            'animatedAtlasFrames':32,'frameDurationMs':80,'loopMs':2560,'imageAnimationTargetFPS':12.5,
            'usedCounts':[7,8,8,4,5,8,6,6,6,8,8],'unusedCellsTransparent':True,
            'lookRowsVisiblePixelIdenticalToSourceInEveryFrame':True,'staticDefaultVisiblePixelIdenticalToSource':True,
            'roundTripVisibleRGBAIdentical':True,'transparentRGBComparison':'canonicalized to zero; alpha preserved exactly',
            'states':checks,'sourceSha256':sha256((ROOT/'assets/source-spritesheet.webp').read_bytes()).hexdigest(),
            'atlasSha256':sha256(animated.read_bytes()).hexdigest(),'bytes':animated.stat().st_size,
            'runtime':'native animated WebP decoded by the existing CSS background-image; no external process',
            'scope':'file format, all decoded frames, visible source differences; host rendering tested separately'}
    (ROOT/'docs/native-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'frames':decoded.n_frames,'bytes':animated.stat().st_size,'changedStates':[x['state'] for x in checks if x['visibleFramesChanged']]}))

if __name__=='__main__':build()
