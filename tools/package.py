"""Package only what the Codex native pet requires, plus recovery/validation files."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import argparse, hashlib, json, shutil
ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    report=json.loads((ROOT/'docs/native-validation.json').read_text('utf-8'))
    assert report['ok'] and report['animatedAtlasFrames']==32
    assert report['atlasSha256']==hashlib.sha256((ROOT/'assets/spritesheet.webp').read_bytes()).hexdigest()
    assert json.loads((ROOT/'docs/native-browser-validation.json').read_text('utf-8'))['ok']
    assert (ROOT/'docs/native-visual-qa.md').exists()
    entries={'pet.json':'pet.json','assets/spritesheet.webp':'spritesheet.webp',
             'assets/static-spritesheet.webp':'static-spritesheet.webp',
             'Install-Codex.cmd':'Install-Codex.cmd','Install-Codex.ps1':'Install-Codex.ps1',
             'README.md':'README.md','THIRD-PARTY.md':'THIRD-PARTY.md',
             'docs/native-validation.json':'docs/native-validation.json',
             'docs/native-browser-validation.json':'docs/native-browser-validation.json',
             'docs/native-visual-qa.md':'docs/native-visual-qa.md',
             'docs/native-previews/idle.gif':'docs/native-previews/idle.gif',
             'docs/native-preview.png':'docs/native-preview.png',
             'web/rig/LICENSE':'LICENSES/Anime2.5DRig.txt'}
    archive=args.out/'Miku-Mini-Codex-pet.zip'
    with ZipFile(archive,'w',ZIP_DEFLATED,compresslevel=6) as bundle:
        for source,dest in entries.items():bundle.write(ROOT/source,'Miku-Mini-Codex/'+dest)
    with ZipFile(archive) as bundle:assert bundle.testzip() is None
    shutil.copy2(ROOT/'docs/native-previews/idle.gif',args.out/'Miku-Mini-Codex-idle.gif')
    shutil.copy2(ROOT/'docs/native-preview.png',args.out/'Miku-Mini-Codex-preview.png')
    shutil.copy2(ROOT/'README.md',args.out/'Miku-Mini-Codex-使用说明.md')
    note={'package':archive.name,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),
          'bytes':archive.stat().st_size,'type':'Codex v2 native pet, animated WebP with static fallback',
          'gitHubUpdate':'pending native update push'}
    (args.out/'native-package-info.json').write_text(json.dumps(note,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(note,ensure_ascii=False))

if __name__=='__main__':main()
