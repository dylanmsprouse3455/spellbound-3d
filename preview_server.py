from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parent
SETTINGS=ROOT/'orb-preview-settings.json'
LIMITS={'size':(.5,2.5),'glow':(.2,3),'speed':(.1,1.5)}
class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs): super().__init__(*args,directory=str(ROOT),**kwargs)
    def do_GET(self):
        if self.path.split('?')[0]=='/api/orb-settings':
            return self.json_response(200,json.loads(SETTINGS.read_text()) if SETTINGS.exists() else {'size':1,'glow':1,'speed':.36})
        return super().do_GET()
    def json_response(self,code,data):
        body=json.dumps(data).encode();self.send_response(code);self.send_header('Content-Type','application/json');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
    def do_POST(self):
        if self.path!='/api/orb-settings':return self.json_response(404,{'error':'Not found'})
        try:
            n=int(self.headers.get('Content-Length','0'))
            if n<1 or n>2048:raise ValueError('Invalid payload')
            data=json.loads(self.rfile.read(n));out={}
            for k,(low,high) in LIMITS.items():
                v=float(data[k]);
                if not low<=v<=high:raise ValueError('Out of range: '+k)
                out[k]=v
            temp=SETTINGS.with_suffix('.tmp');temp.write_text(json.dumps(out,indent=2)+'\n');temp.replace(SETTINGS)
            self.json_response(200,{'saved':True,'settings':out})
        except (ValueError,KeyError,TypeError,json.JSONDecodeError) as e:self.json_response(400,{'error':str(e)})
if __name__=='__main__':ThreadingHTTPServer(('0.0.0.0',8765),Handler).serve_forever()
