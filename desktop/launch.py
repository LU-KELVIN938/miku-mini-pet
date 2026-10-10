"""Small pywebview host; Codex record parsing is reused from Codex-desktop-pet.

Launching opens one transparent pet window. No global mouse tracking, camera,
microphone, startup registration or account credentials are used.
"""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import argparse, json, sys, threading, time
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'desktop/vendor'))

def main():
    p=argparse.ArgumentParser();p.add_argument('--state-only',action='store_true');p.add_argument('--no-codex',action='store_true')
    p.add_argument('--verify-window',action='store_true',help='Open, verify this pet window only, then close it')
    args=p.parse_args()
    if args.state_only:
        import codex_state
        print(json.dumps({'state':codex_state.snapshot().get('state','idle')},ensure_ascii=False));return
    import webview
    class QuietHandler(SimpleHTTPRequestHandler):
        def log_message(self,*_):pass
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(QuietHandler,directory=str(ROOT/'web')))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    stopped=threading.Event()
    class API:
        def quit(self):window.destroy()
    window=webview.create_window('Miku Mini',f'http://127.0.0.1:{server.server_port}/?desktop=1',
        width=270,height=332,frameless=True,transparent=True,on_top=True,easy_drag=True,js_api=API())
    window.events.closed+=lambda:stopped.set()
    def watch():
        if args.verify_window:
            result={'ok':False,'scope':'actual pywebview EdgeChromium window; no screen capture','states':[]}
            try:
                deadline=time.monotonic()+60
                while time.monotonic()<deadline and not stopped.wait(.3):
                    if window.evaluate_js('!!window.MikuMini && window.MikuMini.state().rigReady'):break
                else:raise RuntimeError('Pet renderer did not become ready')
                result['transparentBackground']=window.evaluate_js("getComputedStyle(document.documentElement).backgroundColor")
                for state in ['idle','running','waiting','review','running-right','running-left','waving','jumping','failed']:
                    window.evaluate_js('window.MikuMini.setState('+json.dumps(state)+')')
                    time.sleep(.4)
                    snapshot=window.evaluate_js('window.MikuMini.state()')
                    assert snapshot['state']==state and snapshot['rigReady']
                    assert snapshot['activeLayered']==(state in ['idle','running','waiting','review'])
                    result['states'].append(snapshot)
                assert result['transparentBackground']=='rgba(0, 0, 0, 0)'
                result['ok']=True
            except Exception as error:result['error']=str(error)
            finally:
                path=ROOT/'docs/desktop-validation.json'
                path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
                print(json.dumps(result,ensure_ascii=False),flush=True)
                window.destroy()
            return
        if args.no_codex:return
        import codex_state
        last=None
        while not stopped.wait(.8):
            try:
                state=codex_state.snapshot().get('state','idle')
                if state!=last:
                    ready=window.evaluate_js('!!window.MikuMini')
                    if ready:
                        window.evaluate_js('window.MikuMini.receiveCodex('+json.dumps({'state':state})+')')
                        last=state
            except Exception:
                # A parser/database failure leaves the already-playing idle loop intact.
                continue
    try:webview.start(watch,gui='edgechromium',private_mode=True)
    finally:stopped.set();server.shutdown();server.server_close()

if __name__=='__main__':main()
