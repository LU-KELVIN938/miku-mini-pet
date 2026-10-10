"""Register existing sprites and cut existing character art into editable parts.

No image generation or new pose synthesis. Pillow + NumPy only.
"""
from pathlib import Path
import argparse, hashlib, json, shutil
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
STATES = ['idle','running-right','running-left','waving','jumping','failed','waiting','running','review']
COUNTS = [6,8,8,4,5,8,6,6,6]
DURATIONS = [[280,110,110,140,140,320],[120]*7+[220],[120]*7+[220],[140]*3+[280],
             [140]*4+[280],[140]*7+[240],[150]*5+[260],[120]*5+[220],[150]*5+[280]]

def save_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def cut_key(image):
    arr = np.array(image.convert('RGB'), dtype=np.float32)
    dist = np.linalg.norm(arr-np.array([255,0,255]), axis=2)
    a = np.clip((dist-25)/80,0,1)
    rgb = arr.copy(); known = a >= .99
    # Edge RGB dilation keeps the new matte free of key-colored fringes.
    for _ in range(8):
        previous = known.copy()
        for dy, dx in [(-1,0),(1,0),(0,-1),(0,1)]:
            shifted = np.roll(previous,(dy,dx),(0,1))
            if dy == -1: shifted[-1,:] = False
            if dy == 1: shifted[0,:] = False
            if dx == -1: shifted[:,-1] = False
            if dx == 1: shifted[:,0] = False
            take = (~known) & shifted
            rgb[take] = np.roll(rgb,(dy,dx),(0,1))[take]
            known[take] = True
    rgb[a==0] = 0
    return Image.fromarray(np.dstack([rgb,(a*255)]).astype('uint8'))

def prepare_atlas():
    source = ROOT/'assets/source-spritesheet.webp'
    if not source.exists(): shutil.copy2(ROOT/'assets/spritesheet.webp',source)
    atlas = Image.open(source).convert('RGBA'); result = atlas.copy()
    rows=[]; records=[]
    for row,(state,n,durations) in enumerate(zip(STATES,COUNTS,DURATIONS)):
        frames=[atlas.crop((c*192,row*208,(c+1)*192,(row+1)*208)) for c in range(n)]
        # Only one-pixel horizontal registration; intentional vertical motion stays.
        centers=[(im.getbbox()[0]+im.getbbox()[2])/2 for im in frames]
        target=float(np.median(centers))
        stable=state in {'idle','running-right','running-left','waving','waiting','running'}
        for c,frame in enumerate(frames):
            dx=int(np.clip(round(target-centers[c]),-2,2)) if stable else 0
            fixed=Image.new('RGBA',frame.size)
            fixed.paste(frame,(dx,0))
            assert np.array(fixed.getchannel('A')).sum()==np.array(frame.getchannel('A')).sum(), 'clipped sprite'
            result.paste(fixed,(c*192,row*208))
            out=ROOT/f'web/frames/{state}/{c:02d}.png'; out.parent.mkdir(parents=True,exist_ok=True); fixed.save(out)
            records.append({'state':state,'frame':c,'dx':dx,'dy':0,'scale':1})
        rows.append({'state':state,'row':row,'count':n,'durations':durations,
                     'frames':[f'frames/{state}/{c:02d}.png' for c in range(n)]})
    assert np.array_equal(np.array(atlas)[9*208:],np.array(result)[9*208:])
    result.save(ROOT/'assets/spritesheet.webp',lossless=True,exact=True)
    result.save(ROOT/'assets/contact-sheet.png')
    shutil.copy2(source,ROOT/'web/source-spritesheet.webp')
    save_json(ROOT/'web/animations.json',{'cell':[192,208],'states':rows,'interpolation':{}})
    save_json(ROOT/'docs/registration.json',{'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'changes':records,'lookRowsUnchanged':True,'verticalMotionUnchanged':True,'nativeFrameCountsUnchanged':True})
    return result

def polygon(points,size=(600,649)):
    m=Image.new('L',size); ImageDraw.Draw(m).polygon(points,fill=255); return np.array(m)>0

def prepare_layers(base_path):
    image=cut_key(Image.open(base_path).resize((600,649),Image.Resampling.LANCZOS))
    original=np.array(image); arr=original.copy()
    head=polygon([(200,60),(243,40),(267,27),(302,28),(282,57),(341,65),(398,46),
        (425,111),(419,185),(414,237),(382,275),(335,294),(264,294),(220,289),
        (184,247),(158,218),(163,175),(158,138),(158,92),(183,59)])
    body=polygon([(270,285),(325,285),(342,300),(379,328),(443,347),(464,359),
        (457,381),(422,393),(391,364),(346,345),(384,416),(353,454),(349,535),
        (334,637),(295,637),(297,526),(296,464),(277,516),(245,615),(216,620),
        (190,590),(216,544),(238,487),(243,449),(211,423),(220,390),(252,354),
        (231,333),(210,356),(187,400),(162,407),(128,378),(124,347),(145,334),
        (210,317),(247,296)]) & ~head
    tail=(~head)&(~body); x=np.indices(head.shape)[1]
    masks={'back hair_1':tail&(x<300),'back hair_2':tail&(x>=300),'topwear':body,'face':head}
    eyes=[[(218,204),(234,198),(253,199),(267,210),(273,225),(269,244),(254,253),(234,249),(220,236)],
          [(311,202),(322,191),(347,190),(364,201),(369,217),(360,239),(339,244),(319,233)]]
    eye_mask=polygon(eyes[0])|polygon(eyes[1]); masks['eyewhite']=eye_mask
    # Fill only the eye aperture in the underlying face, by cloning local skin.
    for points,sample in zip(eyes,[(278,252),(373,247)]):
        m=polygon(points); sx,sy=sample
        color=np.median(original[sy-3:sy+4,sx-3:sx+4,:3].reshape(-1,3),axis=0)
        arr[m,:3]=color
    scratch=ROOT/'work/layers'; scratch.mkdir(parents=True,exist_ok=True)
    manifest={'width':600,'height':649,'children':[]}
    layer_dir=ROOT/'assets/layers'; layer_dir.mkdir(parents=True,exist_ok=True)
    for name,m in masks.items():
        pixels=(original if name=='eyewhite' else arr).copy(); pixels[~m]=0
        layer=Image.fromarray(pixels); box=layer.getbbox()
        if not box: continue
        crop=layer.crop(box); stem=name.replace(' ','-')
        crop.save(layer_dir/f'{stem}.png'); raw=scratch/f'{stem}.rgba'; raw.write_bytes(crop.tobytes())
        manifest['children'].append({'name':name,'left':box[0],'top':box[1],
            'width':crop.width,'height':crop.height,'raw':str(raw)})
    # Closed lids come from the pet's existing blink frame, not a generic eye asset.
    closed=Image.open(ROOT/'assets/source-spritesheet.webp').convert('RGBA').crop((192,0,384,208))
    lids=Image.new('RGBA',(600,649))
    for src,dst in [((71,72,94,81),(216,224,275,247)),((101,67,124,76),(311,215,370,238))]:
        patch=np.array(closed.crop(src)); dark=np.clip((155-patch[:,:,:3].mean(axis=2))/85,0,1)
        patch[:,:,3]=(patch[:,:,3]*dark).astype('uint8'); patch[patch[:,:,3]==0,:3]=0
        part=Image.fromarray(patch).resize((dst[2]-dst[0],dst[3]-dst[1]),Image.Resampling.LANCZOS)
        lids.alpha_composite(part,(dst[0],dst[1]))
    box=lids.getbbox(); crop=lids.crop(box); crop.save(layer_dir/'eye-close.png')
    raw=scratch/'eye-close.rgba'; raw.write_bytes(crop.tobytes())
    manifest['children'].append({'name':'eye_close','left':box[0],'top':box[1],
        'width':crop.width,'height':crop.height,'raw':str(raw)})
    composite=scratch/'composite.rgba'; composite.write_bytes(image.tobytes())
    manifest['composite']=str(composite)
    save_json(scratch/'manifest.json',manifest)
    image.save(ROOT/'assets/layered-reference.png')
    save_json(ROOT/'docs/layer-provenance.json',{'method':'deterministic masks of existing canonical artwork',
        'closedEyes':'existing idle blink frame','eyeBase':'local skin pixels cloned inside original eye aperture',
        'generatedImages':0,'layers':list(masks)+['eye_close'],
        'scope':'small head movement, breathing, blink and twin-tail sway; not full Live2D'})

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--base',type=Path,required=True)
    args=parser.parse_args(); prepare_atlas(); prepare_layers(args.base)
    print('Registered native atlas and prepared six source-art layers.')
