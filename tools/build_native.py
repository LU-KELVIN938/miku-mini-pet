"""Restore the user's original walking poses in a lossless static v2 atlas.

Codex controls the eight movement cells. No independent image animation clock.
"""
from pathlib import Path
from hashlib import sha256
import json, shutil
import numpy as np
from PIL import Image, ImageDraw
from build_gait_candidate import visible_rgba, verify

ROOT = Path(__file__).resolve().parents[1]
STATES = ['idle','running-right','running-left','waving','jumping','failed','waiting','running','review']
COUNTS = [6,8,8,4,5,8,6,6,6]
DURATIONS = [[1680,660,660,840,840,1920],[120]*7+[220],[120]*7+[220],
             [140]*3+[280],[140]*4+[280],[140]*7+[240],[150]*5+[260],[120]*5+[220],[150]*5+[280]]


def build():
    with Image.open(ROOT/'assets/native-micro-base.webp') as im:
        base = Image.fromarray(visible_rgba(im))
    with Image.open(ROOT/'assets/source-spritesheet.webp') as im:
        source = Image.fromarray(visible_rgba(im))
    atlas = base.copy()
    pose_hashes = {}
    for row,state in [(1,'running-right'),(2,'running-left')]:
        strip = source.crop((0,row*208,1536,(row+1)*208))
        atlas.paste(strip,(0,row*208))
        pose_hashes[state] = sha256(visible_rgba(strip).tobytes()).hexdigest()
    atlas = Image.fromarray(visible_rgba(atlas))
    output = ROOT/'assets/spritesheet.webp'
    atlas.save(output,lossless=True,exact=True)
    with Image.open(output) as decoded:
        report = verify(decoded,base)
        assert np.array_equal(visible_rgba(decoded),visible_rgba(atlas)), 'Encoding changed visible pixels'
        assert np.array_equal(visible_rgba(decoded)[1872:],visible_rgba(source)[1872:]), 'Original look directions changed'
        assert np.array_equal(visible_rgba(decoded)[208:624],visible_rgba(source)[208:624]), 'Original walking artwork changed'
    ready = True  # User explicitly requested original gestures, including their original cadence.
    report.update({'atlasSha256':sha256(output.read_bytes()).hexdigest(),'bytes':output.stat().st_size,
      'animatedAtlasFrames':1,'imageFrames':1,'playbackClock':'Codex native cell timer only',
      'locomotionPoseHashes':pose_hashes,'baseSha256':sha256((ROOT/'assets/native-micro-base.webp').read_bytes()).hexdigest(),
      'lookRowsVisibleRGBAIdenticalToOriginalSource':True,
      'nonLocomotionRowsVisibleRGBAIdenticalToApprovedMicroBase':True,
      'originalWalkingVisibleRGBAIdenticalToSource':True,'originalWalkingColumnOrderPreserved':True,
      'movementResamplingOrInterpolation':False,'userRequestedOriginalActions':True,
      'releaseReady':bool(ready),'releaseScope':'original artwork restoration and lossless single-clock packaging; not measured desktop frame drops',
      'acceptedVisualWarnings':['original action and limited frame cadence retained at user request'],
      'actualCodexWindowVerified':False,
      'hostLimitations':['directional action falls back to idle after three cycles in inspected app version',
                         'release and reversal can interrupt a cycle','final movement cell holds 220ms'],
      'priorAnimatedAtlasBytes':44272996})
    (ROOT/'docs/native-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    shutil.copy2(output,ROOT/'assets/static-spritesheet.webp')
    shutil.copy2(output,ROOT/'web/native-spritesheet.webp')
    dest = ROOT/'docs/native-previews';dest.mkdir(exist_ok=True)
    for row,state in enumerate(STATES):
        frames=[]
        for col in range(COUNTS[row]):
            cell=atlas.crop((col*192,row*208,(col+1)*192,(row+1)*208))
            bg=Image.new('RGBA',(192,208),'#ecf6f3');bg.alpha_composite(cell);frames.append(bg.convert('RGB'))
        frames[0].save(dest/f'{state}.gif',save_all=True,append_images=frames[1:],duration=DURATIONS[row],loop=0)
    look=atlas.crop((4*192,9*208,5*192,10*208))
    bg=Image.new('RGBA',(192,208),'#ecf6f3');bg.alpha_composite(look);bg.convert('RGB').save(dest/'look-right.gif')
    sheet=Image.new('RGB',(1536,940),'#ecf6f3');draw=ImageDraw.Draw(sheet)
    for index,row in enumerate([1,2,0,7]):
        draw.text((5,index*235+3),STATES[row],fill='#284d56')
        for col in range(COUNTS[row]):
            cell=atlas.crop((col*192,row*208,(col+1)*192,(row+1)*208))
            sheet.paste(cell,(col*192,index*235+25),cell)
    sheet.save(ROOT/'docs/native-motion-sheet.png')
    print(json.dumps({'imageFrames':1,'bytes':report['bytes'],'originalActionsRestored':True,'releaseReady':ready}))


if __name__ == '__main__':
    build()
