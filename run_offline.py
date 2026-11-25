from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import sqlite3, json, math, html
from urllib.parse import parse_qs
from pathlib import Path
DB=Path(__file__).with_name('offline.db')
def evaluate(rain,wind):
    if not all(math.isfinite(x) and x>=0 for x in (rain,wind)): raise ValueError('Invalid readings')
    return [n for n,c in [('FLOOD',rain>=100),('STORM',wind>=75)] if c]
def init():
    with sqlite3.connect(DB) as c: c.execute('CREATE TABLE IF NOT EXISTS alerts(district TEXT,hazard TEXT,delay REAL,status TEXT)')
class Handler(BaseHTTPRequestHandler):
    def reply(self,data,status=200,kind='application/json'):
        b=(json.dumps(data) if kind=='application/json' else data).encode(); self.send_response(status); self.send_header('Content-Type',kind+'; charset=utf-8'); self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        with sqlite3.connect(DB) as c: rows=c.execute('SELECT * FROM alerts ORDER BY rowid DESC').fetchall()
        if self.path=='/api/health': return self.reply({'status':'ok'})
        if self.path=='/api/monitor': return self.reply({'total':len(rows),'late':sum(r[3]=='LATE' for r in rows),'simulated':True})
        if self.path!='/': return self.reply({'error':'Not found'},404)
        page=Path(__file__).with_name('templates').joinpath('index.html').read_text(encoding='utf-8'); import re
        table=''.join('<tr>'+''.join('<td>'+html.escape(str(v))+'</td>' for v in r)+'<td>—</td></tr>' for r in rows)
        page=re.sub(r'{% for a in alerts %}.*?{% endfor %}',lambda _:table,page); page=page.replace('{{alerts|length}}',str(len(rows))).replace('{{late}}',str(sum(r[3]=='LATE' for r in rows))); self.reply(page,kind='text/html')
    def do_POST(self):
        if self.path!='/api/alerts': return self.reply({'error':'Not found'},404)
        try:
            raw=self.rfile.read(int(self.headers.get('Content-Length',0))); ct=self.headers.get('Content-Type','')
            if 'application/json' in ct: d=json.loads(raw)
            else: d={k:v[0] for k,v in parse_qs(raw.decode()).items()}
            district=d['district'].strip(); rain=float(d['rain']); wind=float(d['wind']); delay=float(d.get('delay',0)); hazards=evaluate(rain,wind)
            if not district or len(district)>100 or not math.isfinite(delay) or delay<0: raise ValueError()
        except (ValueError,KeyError,TypeError,AttributeError): return self.reply({'error':'Invalid input'},400)
        status='ON TIME' if delay<600 else 'LATE'
        with sqlite3.connect(DB) as c: c.executemany('INSERT INTO alerts VALUES (?,?,?,?)',[(district,h,delay,status) for h in hazards])
        self.reply(dict(hazards=hazards,status=status if hazards else 'SAFE',target_residents=200000,channels=['SMS','APP'],simulated=True))
if __name__=='__main__':
    init(); print('Open http://127.0.0.1:5000',flush=True); ThreadingHTTPServer(('127.0.0.1',5000),Handler).serve_forever()
