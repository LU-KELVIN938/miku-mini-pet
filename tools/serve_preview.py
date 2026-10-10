"""Serve only the pet's public web files on loopback; opens no browser."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import argparse
ROOT=Path(__file__).resolve().parents[1]
class PetHandler(SimpleHTTPRequestHandler):
    def translate_path(self,path):
        if path.split('?',1)[0]=='/native-spritesheet.webp':return str(ROOT/'assets/spritesheet.webp')
        if path.split('?',1)[0]=='/native-candidate.webp':return str(ROOT/'work/gait-repair/candidate-spritesheet.webp')
        return super().translate_path(path)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=8765);args=p.parse_args()
    print(f'Pet preview: http://127.0.0.1:{args.port}/',flush=True)
    ThreadingHTTPServer(('127.0.0.1',args.port),partial(PetHandler,directory=str(ROOT/'web'))).serve_forever()
