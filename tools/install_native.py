"""Install native atlas with an explicit timestamped backup; opens no window."""
from pathlib import Path
from datetime import datetime
import argparse, json, shutil
ROOT=Path(__file__).resolve().parents[1]
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--backup-dir',type=Path,default=ROOT/'outputs',help='Directory for timestamped restore copies')
    args=parser.parse_args()
    destination=Path.home()/'.codex/pets/miku-mini'
    backup=args.backup_dir/('native-backup-'+datetime.now().strftime('%Y%m%d-%H%M%S'))
    backup.mkdir(parents=True,exist_ok=False)
    for name in ['pet.json','spritesheet.webp']:
        if (destination/name).exists():shutil.copy2(destination/name,backup/name)
    destination.mkdir(parents=True,exist_ok=True)
    meta=json.loads((ROOT/'pet.json').read_text('utf-8'));meta['spritesheetPath']='spritesheet.webp'
    (destination/'pet.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    shutil.copy2(ROOT/'assets/spritesheet.webp',destination/'spritesheet.webp')
    print('Installed native compatibility version; backup:',backup)
if __name__=='__main__':main()
