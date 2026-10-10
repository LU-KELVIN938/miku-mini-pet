from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1]
def main():
    config=json.loads((ROOT/'web/animations.json').read_text('utf-8'))
    dest=ROOT/'docs/previews';dest.mkdir(exist_ok=True)
    for row in config['states']:
        seq=config['interpolation'].get(row['state'],row);frames=[]
        for path in seq['frames']:
            im=Image.open(ROOT/'web'/path).convert('RGBA');bg=Image.new('RGBA',im.size,(236,246,243,255));bg.alpha_composite(im);frames.append(bg.convert('RGB'))
        frames[0].save(dest/f"{row['state']}.gif",save_all=True,append_images=frames[1:],duration=seq['durations'],loop=0)
    source=Image.open(ROOT/'assets/source-spritesheet.webp').convert('RGBA')
    atlas=Image.open(ROOT/'assets/spritesheet.webp').convert('RGBA')
    # This existing atlas also reserves row 0, column 6 for its static default pose.
    used=[7,8,8,4,5,8,6,6,6,8,8];labels=[r['state'] for r in config['states']]+['look A','look B']
    contact=Image.new('RGB',(920,1154),'#edf5f3');draw=ImageDraw.Draw(contact)
    for r,n in enumerate(used):
        draw.text((10,r*104+45),labels[r],fill='#31515b')
        for c in range(n):
            cell=atlas.crop((c*192,r*208,(c+1)*192,(r+1)*208)).resize((96,104),Image.Resampling.LANCZOS)
            contact.paste(cell,(145+c*96,r*104),cell)
        for c in range(n,8):assert not atlas.crop((c*192,r*208,(c+1)*192,(r+1)*208)).getbbox()
    contact.save(ROOT/'assets/contact-sheet.png')
    assert atlas.size==(1536,2288)
    assert np.array_equal(np.array(atlas)[1872:],np.array(source)[1872:])
    (ROOT/'docs/native-validation.json').write_text(json.dumps({'ok':True,'size':list(atlas.size),'usedCounts':used,
        'unusedCellsTransparent':True,'lookRowsPixelIdenticalToSource':True,'scope':'geometry, alpha preservation and format; motion checked separately'},indent=2)+'\n',encoding='utf-8')
    captures=sorted((ROOT/'work/rig-captures').glob('*.png'))
    if captures:
        frames=[]
        for f in captures:
            im=Image.open(f).convert('RGBA');im.thumbnail((192,208),Image.Resampling.LANCZOS)
            bg=Image.new('RGBA',(192,208),(236,246,243,255));bg.alpha_composite(im,((192-im.width)//2,(208-im.height)//2));frames.append(bg.convert('RGB'))
        frames[0].save(dest/'layered-idle.gif',save_all=True,append_images=frames[1:],duration=40,loop=0)
    print('Generated transparent-format checks, contact sheet and animation previews.')
if __name__=='__main__':main()
