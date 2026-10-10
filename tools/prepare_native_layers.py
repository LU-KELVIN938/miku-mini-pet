"""Cut the existing native idle sprite into motion layers, preserving its style."""
from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[1]

def polygon(points):
    mask=Image.new('L',(192,208));ImageDraw.Draw(mask).polygon(points,fill=255)
    return np.array(mask)>0

def main():
    source=Image.open(ROOT/'assets/source-spritesheet.webp').convert('RGBA')
    neutral=source.crop((0,0,192,208));original=np.array(neutral);face_pixels=original.copy()
    head=polygon([(62,21),(76,17),(79,5),(91,4),(86,16),(111,19),(121,13),(126,31),
                  (140,58),(130,85),(113,93),(89,93),(70,94),(60,79),(54,60),(52,45)])
    body=polygon([(87,93),(107,91),(117,101),(145,113),(150,122),(144,131),(130,128),
                  (116,114),(126,138),(117,154),(114,202),(96,203),(94,172),(84,188),
                  (74,198),(61,190),(74,166),(88,150),(78,143),(69,135),(81,117),
                  (75,111),(59,128),(45,131),(42,122),(48,117),(74,103)])&~head
    eyes=polygon([(70,64),(78,60),(88,62),(94,69),(94,81),(85,86),(74,82)])|polygon([(100,60),(108,55),(116,56),(124,63),(124,77),(115,82),(105,79)])
    for points,sample in [([(70,64),(78,60),(88,62),(94,69),(94,81),(85,86),(74,82)],(96,77)),
                          ([(100,60),(108,55),(116,56),(124,63),(124,77),(115,82),(105,79)],(106,81))]:
        x,y=sample;color=np.median(original[y-1:y+2,x-1:x+2,:3].reshape(-1,3),axis=0)
        face_pixels[polygon(points),:3]=color
    tail=~head&~body;x=np.indices(head.shape)[1]
    masks={'back hair_1':tail&(x<96),'back hair_2':tail&(x>=96),'topwear':body,'face':head,'eyewhite':eyes}
    work=ROOT/'work/native-layers';work.mkdir(parents=True,exist_ok=True)
    manifest={'width':576,'height':624,'children':[]}
    for name,mask in masks.items():
        pixels=(face_pixels if name=='face' else original).copy();pixels[~mask]=0
        im=Image.fromarray(pixels).resize((576,624),Image.Resampling.NEAREST)
        box=im.getbbox();crop=im.crop(box);raw=work/(name.replace(' ','-')+'.rgba');raw.write_bytes(crop.tobytes())
        manifest['children'].append({'name':name,'left':box[0],'top':box[1],'width':crop.width,'height':crop.height,'raw':str(raw)})
    blink=source.crop((192,0,384,208));lids=Image.new('RGBA',(192,208))
    for box in [(71,72,94,81),(101,67,124,76)]:
        patch=np.array(blink.crop(box));dark=np.clip((155-patch[:,:,:3].mean(axis=2))/85,0,1)
        patch[:,:,3]=(patch[:,:,3]*dark).astype('uint8');patch[patch[:,:,3]==0,:3]=0
        lids.alpha_composite(Image.fromarray(patch),box[:2])
    im=lids.resize((576,624),Image.Resampling.NEAREST);box=im.getbbox();crop=im.crop(box)
    raw=work/'eye-close.rgba';raw.write_bytes(crop.tobytes())
    manifest['children'].append({'name':'eye_close','left':box[0],'top':box[1],'width':crop.width,'height':crop.height,'raw':str(raw)})
    raw=work/'composite.rgba';raw.write_bytes(neutral.resize((576,624),Image.Resampling.NEAREST).tobytes())
    manifest['composite']=str(raw)
    (work/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print('Six motion layers cut from the original Codex idle frame.')

if __name__=='__main__':main()
