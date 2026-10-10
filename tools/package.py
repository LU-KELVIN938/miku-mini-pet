"""Package reviewed Git-visible files only; exclude scratch, credentials and caches."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import argparse, hashlib, json, shutil, subprocess
from PIL import Image
import numpy as np
ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    source=np.array(Image.open(ROOT/'assets/source-spritesheet.webp').convert('RGBA'))
    native=np.array(Image.open(ROOT/'assets/spritesheet.webp').convert('RGBA'))
    assert native.shape==(2288,1536,4)
    assert np.array_equal(source[1872:],native[1872:])
    assert np.array_equal(source[:208,1152:1344],native[:208,1152:1344])
    report=json.loads((ROOT/'docs/native-validation.json').read_text('utf-8'))
    report['staticDefaultPixelIdenticalToSource']=True
    (ROOT/'docs/native-validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    for name in ['player','desktop']:
        assert json.loads((ROOT/f'docs/{name}-validation.json').read_text('utf-8'))['ok']
    files=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z'],cwd=ROOT).decode('utf-8').split('\0')
    archive=args.out/'Miku-Mini-lightweight.zip'
    with ZipFile(archive,'w',ZIP_DEFLATED,compresslevel=6) as bundle:
        for name in sorted(set(filter(None,files))):
            path=Path(name)
            assert not any(part in {'.git','work','outputs','__pycache__','.venv'} for part in path.parts)
            assert path.suffix.lower() not in {'.key','.pem','.pyc'} and not path.name.startswith('.env')
            if (ROOT/path).is_file():bundle.write(ROOT/path,'Miku-Mini/'+path.as_posix())
    shutil.copy2(ROOT/'docs/previews/layered-idle.gif',args.out/'Miku-Mini-idle.gif')
    shutil.copy2(ROOT/'docs/player-preview.png',args.out/'Miku-Mini-comparison.png')
    shutil.copy2(ROOT/'README.md',args.out/'Miku-Mini-使用说明.md')
    note={'package':archive.name,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),
          'bytes':archive.stat().st_size,'nativeInstallation':'backed up and installed separately',
          'gitHubUpdate':'pending authentication; check live repository for publication status'}
    (args.out/'package-info.json').write_text(json.dumps(note,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(note,ensure_ascii=False))

if __name__=='__main__':main()
