"""Offline 2x RIFE interpolation, with a separate alpha pass and loop closure."""
from pathlib import Path
import argparse, hashlib, json, subprocess, time
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]

def run_rife(exe,model,a,b,out):
    proc=subprocess.run([str(exe),'-0',str(a),'-1',str(b),'-o',str(out),'-m',str(model),
                         '-g','-1','-j','1:2:1'],capture_output=True,text=True,timeout=120)
    if proc.returncode or not out.exists(): raise RuntimeError(proc.stderr[-1500:])

def main():
    p=argparse.ArgumentParser();p.add_argument('--exe',type=Path,required=True)
    p.add_argument('--model',type=Path,required=True);p.add_argument('--states',nargs='+',default=['running-right','running-left','waving'])
    p.add_argument('--method',choices=['key','separate-alpha'],default='separate-alpha')
    args=p.parse_args();config_path=ROOT/'web/animations.json';config=json.loads(config_path.read_text('utf-8'))
    work=ROOT/'work/interpolation';work.mkdir(parents=True,exist_ok=True)
    policy=json.loads((ROOT/'docs/interpolation-policy.json').read_text('utf-8'))
    actual_hash=hashlib.sha256((ROOT/'assets/source-spritesheet.webp').read_bytes()).hexdigest()
    if actual_hash!=policy['sourceSha256']:raise RuntimeError('Source art changed; obtain a fresh visual review before using the saved acceptance policy.')
    report={'engine':'nihui/rife-ncnn-vulkan 20221029','model':args.model.name,'device':'CPU',
            'alpha':'single RGB/key-background pass with matching matte' if args.method=='key' else 'separate RIFE alpha pass',
            'loopClosure':True,'states':[]};start=time.monotonic()
    for state in args.states:
        row=next(r for r in config['states'] if r['state']==state)
        frames=[Image.open(ROOT/'web'/f).convert('RGBA') for f in row['frames']]
        outdir=ROOT/'web/interpolated'/state;outdir.mkdir(parents=True,exist_ok=True)
        rgb_paths=[];alpha_paths=[]
        for i,frame in enumerate(frames):
            a=np.array(frame,dtype=np.float32);alpha=a[:,:,3:4]/255
            rgb=Image.fromarray((a[:,:,:3]*alpha+(1-alpha)*np.array([255,0,255]) if args.method=='key' else a[:,:,:3]*alpha).astype('uint8'))
            mask=Image.fromarray(np.repeat(a[:,:,3:4],3,2).astype('uint8'))
            rgb_path=work/f'{state}-{i}-{args.method}-rgb.png';mask_path=work/f'{state}-{i}-alpha.png'
            rgb.save(rgb_path);mask.save(mask_path);rgb_paths.append(rgb_path);alpha_paths.append(mask_path)
        paths=[];durations=[]
        rejected=policy['rejectedPairs'].get(state,[]) if args.model.name==policy['model'] else []
        for i,frame in enumerate(frames):
            next_i=(i+1)%len(frames);out=outdir/f'{i*2:02d}.png';frame.save(out)
            rgb_out=work/f'{state}-{i}-{args.model.name}-{args.method}-mid-rgb.png';alpha_out=work/f'{state}-{i}-{args.model.name}-mid-alpha.png'
            if not rgb_out.exists():run_rife(args.exe,args.model,rgb_paths[i],rgb_paths[next_i],rgb_out)
            rgb=np.array(Image.open(rgb_out).convert('RGB'),dtype=np.float32)
            if args.method=='key':
                key=np.array([255,0,255]);dist=np.linalg.norm(rgb-key,axis=2)
                alpha=np.clip((dist-30)/90,0,1)*255
                color=np.clip((rgb-key*(1-alpha[:,:,None]/255))*255/np.maximum(alpha[:,:,None],1),0,255)
                # Extend clean foreground color through the translucent edge band.
                known=dist>=150
                for _ in range(5):
                    prior=known.copy()
                    for dy,dx in [(-1,0),(1,0),(0,-1),(0,1)]:
                        neighbor=np.roll(prior,(dy,dx),(0,1));take=(~known)&neighbor
                        color[take]=np.roll(color,(dy,dx),(0,1))[take];known[take]=True
            else:
                if not alpha_out.exists():run_rife(args.exe,args.model,alpha_paths[i],alpha_paths[next_i],alpha_out)
                alpha=np.array(Image.open(alpha_out).convert('RGB'),dtype=np.float32).mean(2)
                alpha[alpha<3]=0
                color=np.minimum(255,rgb*255/np.maximum(alpha[:,:,None],1))
            color[alpha==0]=0
            mid=frame if i in rejected else Image.fromarray(np.dstack([color,alpha]).astype('uint8'))
            mid.save(outdir/f'{i*2+1:02d}.png')
            paths.extend([f'interpolated/{state}/{i*2:02d}.png',f'interpolated/{state}/{i*2+1:02d}.png'])
            duration=row['durations'][i]
            # Preserve intentional long hold, then perform the usual transition.
            transition=min(duration,int(np.median(row['durations'])))
            durations.extend([duration-transition/2,transition/2])
            print(f'{state}: {i+1}/{len(frames)} pairs',flush=True)
        assert sum(durations)==sum(row['durations'])
        config['interpolation'][state]={'frames':paths,'durations':durations,'originalPoseHoldPairs':rejected}
        report['states'].append({'state':state,'inputFrames':len(frames),'outputFrames':len(paths),
            'loopMs':sum(durations),'includingLastToFirst':True,'originalPoseHoldPairs':rejected,
            'acceptedNewFrames':len(frames)-len(rejected)})
        config_path.write_text(json.dumps(config,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    report['processingSeconds']=round(time.monotonic()-start,2)
    (ROOT/'docs/interpolation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report))

if __name__=='__main__':main()
