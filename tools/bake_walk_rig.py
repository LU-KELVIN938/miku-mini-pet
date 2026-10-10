"""Bake a small-step two-leg rig from existing Miku artwork.

The user explicitly chose reuse of source artwork and programmatic pose baking
instead of image generation. No new character art, image API or paid tool.
"""
from pathlib import Path
import json, math, argparse
import numpy as np
from PIL import Image, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SCALE = 3
SIZE = (192, 208)
DURATIONS = [120]*7 + [220]


def masked(image, points):
    mask = Image.new('L', SIZE)
    ImageDraw.Draw(mask).polygon(points, fill=255)
    data = np.array(image)
    data[:, :, 3] = (data[:, :, 3].astype(float)*np.array(mask)/255).astype('uint8')
    data[data[:, :, 3] == 0, :3] = 0
    return Image.fromarray(data).resize((576,624), Image.Resampling.NEAREST)


def knee_for(hip, ankle, length1, length2):
    dx,dy = ankle[0]-hip[0],ankle[1]-hip[1]
    distance = min(math.hypot(dx,dy), length1+length2-.15)
    along = (length1**2-length2**2+distance**2)/(2*distance)
    height = math.sqrt(max(0,length1**2-along**2))
    ux,uy = dx/math.hypot(dx,dy),dy/math.hypot(dx,dy)
    # A right-facing knee bends toward screen-right.
    return (hip[0]+ux*along+uy*height,hip[1]+uy*along-ux*height)


def leg_target(hip, phase):
    # Half a cycle is planted/weight-bearing, half swings back to front.
    p = phase % 1
    if p < .5:
        x = 14-56*p
        y = 191
    else:
        u = (p-.5)*2
        x = -14+28*u
        y = 191-8*math.sin(math.pi*u)
    ankle = (hip[0]+x, y)
    knee = knee_for(hip, ankle, math.hypot(7,20), math.hypot(6,19))
    return {'hip':hip,'knee':knee,'ankle':ankle,'phase':float(p),
            'stance':bool(p<.5),'footTip':(ankle[0]+11,ankle[1])}


def deform_leg(texture, leg):
    """Continuous textured strip mesh; shared vertices avoid cut-segment seams."""
    hip,knee,ankle=leg['hip'],leg['knee'],leg['ankle']
    angles=[math.atan2(knee[1]-hip[1],knee[0]-hip[0])-math.atan2(20,7),
            math.atan2(ankle[1]-knee[1],ankle[0]-knee[0])-math.atan2(19,6)]
    source_centers=[(116,145),(119,154),(126,174),(132,193),(138,208)]
    upper=(math.cos(angles[0]),math.sin(angles[0]))
    centers=[(hip[0]-3*upper[0]+9*upper[1],hip[1]-3*upper[1]-9*upper[0]),
             hip,knee,ankle,(ankle[0]+6,ankle[1]+15)]
    ring_angles=[angles[0],angles[0],(angles[0]+angles[1])/2,angles[1]/2,0]
    source_vertices=[];vertices=[]
    for center,source_center,angle in zip(centers,source_centers,ring_angles):
        for offset in [-20,20]:
            source_vertices.append((source_center[0]*SCALE+offset*SCALE,source_center[1]*SCALE))
            vertices.append(((center[0]+offset*math.cos(angle))*SCALE,(center[1]+offset*math.sin(angle))*SCALE))
    pixels=np.array(texture,dtype=float)/255
    pixels[:,:,:3]*=pixels[:,:,3:4]
    result=np.zeros_like(pixels)
    for ring in range(4):
        for indexes in [(ring*2,ring*2+1,ring*2+2),(ring*2+1,ring*2+3,ring*2+2)]:
            tri=np.array([vertices[i] for i in indexes]);src=np.array([source_vertices[i] for i in indexes])
            low=np.maximum(np.floor(tri.min(0)).astype(int),0);high=np.minimum(np.ceil(tri.max(0)).astype(int),[575,623])
            if np.any(high<low):continue
            xx,yy=np.meshgrid(np.arange(low[0],high[0]+1),np.arange(low[1],high[1]+1))
            coords=np.stack([xx.ravel(),yy.ravel(),np.ones(xx.size)])
            weights=np.linalg.solve(np.vstack([tri.T,np.ones(3)]),coords)
            inside=(weights>=-1e-6).all(0)
            destx=xx.ravel()[inside];desty=yy.ravel()[inside]
            sample=src.T@weights[:,inside]
            sx=np.clip(sample[0],0,575);sy=np.clip(sample[1],0,623)
            ix=np.floor(sx).astype(int);iy=np.floor(sy).astype(int)
            nx=np.minimum(ix+1,575);ny=np.minimum(iy+1,623)
            fx=(sx-ix)[:,None];fy=(sy-iy)[:,None]
            value=(pixels[iy,ix]*(1-fx)+pixels[iy,nx]*fx)*(1-fy)+(pixels[ny,ix]*(1-fx)+pixels[ny,nx]*fx)*fy
            result[desty,destx]=value
    result[:,:,:3]=result[:,:,:3]/np.maximum(result[:,:,3:4],1e-8)
    return Image.fromarray(np.clip(result*255,0,255).astype('uint8'))


def bake(outdir, mirror_left=False):
    outdir.mkdir(parents=True, exist_ok=True)
    source = Image.open(ROOT/'assets/source-spritesheet.webp').convert('RGBA').crop((0,208,192,416))
    # Source dress hem ends near y=153. The mask removes the original legs while
    # preserving the upper-body art, face, hair and clothing above that hem.
    removal = Image.new('L',SIZE)
    points=[(88,140),(96,145),(103,149),(111,152),(123,154),(134,150),(138,145),
            (155,146),(155,208),(58,208),(58,146),(87,146)]
    ImageDraw.Draw(removal).polygon(points,fill=255)
    pixels=np.array(source);pixels[np.array(removal)>0]=0
    body=Image.fromarray(pixels).resize((576,624),Image.Resampling.NEAREST)
    # The complete foreground leg supplies existing skin, stocking and cyan shoe
    # pixels. Independent near/far bones reuse this texture under the dress.
    whole_leg=masked(source,[(111,152),(130,152),(138,187),(151,190),(153,199),(138,205),(121,204),(110,173)])
    layerdir=outdir/'layers';layerdir.mkdir(exist_ok=True)
    body.resize(SIZE).save(layerdir/'body.png')
    whole_leg.resize(SIZE).save(layerdir/'leg-texture.png')
    frames=[];records=[]
    # Center-of-hold sample positions reflect Codex's long eighth-cell hold.
    starts=np.cumsum([0]+DURATIONS[:-1]); centers=[(s+d/2)/1060 for s,d in zip(starts,DURATIONS)]
    for column,phase in enumerate(centers):
        left=leg_target((107,151),phase)
        right=leg_target((120,155),phase+.5)
        frame=Image.new('RGBA',(576,624))
        for leg in [left,right]:
            frame.alpha_composite(deform_leg(whole_leg,leg))
        frame.alpha_composite(body)
        cell=frame.resize(SIZE,Image.Resampling.LANCZOS)
        a=np.array(cell);a[a[:,:,3]==0,:3]=0;cell=Image.fromarray(a)
        frames.append(cell)
        records.append({'column':column,'durationMs':DURATIONS[column],'phase':round(phase,5),
                        'legs':{'far':left,'near':right}})
        cell.save(outdir/f'right-{column:02d}.png')
    strip=Image.new('RGBA',(1536,208))
    for column,cell in enumerate(frames):strip.paste(cell,(column*192,0))
    strip.save(outdir/'running-right.png')
    if mirror_left:
        mirrored=Image.new('RGBA',strip.size)
        for column,cell in enumerate(frames):mirrored.paste(ImageOps.mirror(cell),(column*192,0))
        mirrored.save(outdir/'running-left.png')
    bgframes=[]
    for cell in frames:
        bg=Image.new('RGBA',SIZE,'#ecf6f3');bg.alpha_composite(cell);bgframes.append(bg.convert('RGB'))
    bgframes[0].save(outdir/'right.gif',save_all=True,append_images=bgframes[1:],duration=DURATIONS,loop=0)
    contact=Image.new('RGB',(1536,500),'#ecf6f3');draw=ImageDraw.Draw(contact)
    for column,cell in enumerate(frames):
        draw.text((column*192+5,4),f'{column} / {DURATIONS[column]} ms',fill='#284d56')
        contact.paste(cell,(column*192,25),cell)
        zoom=cell.crop((65,145,150,208)).resize((170,126),Image.Resampling.NEAREST)
        contact.paste(zoom,(column*192+5,260),zoom)
    contact.save(outdir/'rig-contact.png')
    (outdir/'rig.json').write_text(json.dumps({'source':'assets/source-spritesheet.webp row1 col0',
      'method':'source-art segmented limb textures, inverse-kinematic two-leg gait, deterministic raster bake',
      'userAuthorizedProgrammaticArtworkReuse':True,'generatedImages':0,'durationsMs':DURATIONS,
      'frames':records,'visualQA':'see docs/gait-visual-qa.json',
      'mirrorDecision':('independent right-row QA accepted: no text or handed prop; preserve frame order and timing' if mirror_left else 'pending')},indent=2)+'\n',encoding='utf-8')
    print(outdir/'rig-contact.png')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--outdir',type=Path,default=ROOT/'work/gait-repair/rig');p.add_argument('--mirror-left',action='store_true',help='Use only after the right row and mirroring decision have passed independent visual QA');a=p.parse_args();bake(a.outdir,a.mirror_left)
