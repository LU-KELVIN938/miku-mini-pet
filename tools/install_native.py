"""Install the native-clock Codex v2 atlas with a timestamped backup; opens no window."""
from pathlib import Path
from datetime import datetime
import argparse, json, os, shutil, hashlib
ROOT=Path(__file__).resolve().parents[1]
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--backup-dir',type=Path,default=ROOT/'outputs',help='Directory for timestamped restore copies')
    args=parser.parse_args()
    report=json.loads((ROOT/'docs/native-validation.json').read_text('utf-8'))
    if not report.get('releaseReady'):raise RuntimeError('The full walking rows have not passed release QA')
    actual_hash=hashlib.sha256((ROOT/'assets/spritesheet.webp').read_bytes()).hexdigest()
    browser=json.loads((ROOT/'docs/native-browser-validation.json').read_text('utf-8'))
    if actual_hash!=report['atlasSha256'] or not browser['ok'] or browser['atlasSha256']!=actual_hash:
        raise RuntimeError('Asset hash does not match the validated release')
    visual=json.loads((ROOT/'docs/original-action-visual-qa.json').read_text('utf-8'))
    if not visual['accepted'] or visual['atlasSha256']!=actual_hash:
        raise RuntimeError('Original-action visual review is missing or refers to a different asset')
    destination=Path(os.environ.get('CODEX_HOME',str(Path.home()/'.codex')))/'pets/miku-mini'
    backup=args.backup_dir/('native-backup-'+datetime.now().strftime('%Y%m%d-%H%M%S'))
    backup.mkdir(parents=True,exist_ok=False)
    for name in ['pet.json','spritesheet.webp']:
        if (destination/name).exists():shutil.copy2(destination/name,backup/name)
    destination.mkdir(parents=True,exist_ok=True)
    meta=json.loads((ROOT/'pet.json').read_text('utf-8'));meta['spritesheetPath']='spritesheet.webp'
    (destination/'pet.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    shutil.copy2(ROOT/'assets/spritesheet.webp',destination/'spritesheet.webp')
    print('Installed original-action, native-clock pet; backup:',backup)
    print('Restart Codex and select Miku Mini to reload its previously cached image.')
if __name__=='__main__':main()
