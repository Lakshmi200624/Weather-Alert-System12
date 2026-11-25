import unittest, tempfile, threading, urllib.request, urllib.error, json
from pathlib import Path
import run_offline as app
class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory(); app.DB=Path(cls.tmp.name)/'test.db'; app.init(); cls.server=app.ThreadingHTTPServer(('127.0.0.1',0),app.Handler); cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True); cls.thread.start(); cls.url='http://127.0.0.1:'+str(cls.server.server_port)
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown(); cls.server.server_close(); cls.thread.join(); cls.tmp.cleanup()
    def send(self,**kw):
        data=dict(district='Mysuru',rain=100,wind=0,delay=30)|kw
        return json.load(urllib.request.urlopen(urllib.request.Request(self.url+'/api/alerts',data=json.dumps(data).encode(),headers={'Content-Type':'application/json'})))
    def test_safe(self): self.assertEqual(self.send(rain=99,wind=74)['status'],'SAFE')
    def test_flood(self): self.assertEqual(self.send()['hazards'],['FLOOD'])
    def test_storm(self): self.assertEqual(self.send(rain=0,wind=75)['hazards'],['STORM'])
    def test_both(self): self.assertEqual(self.send(wind=75)['hazards'],['FLOOD','STORM'])
    def test_late(self): self.assertEqual(self.send(delay=600)['status'],'LATE')
    def test_ontime(self): self.assertEqual(self.send(delay=599)['status'],'ON TIME')
    def test_invalid(self):
        with self.assertRaises(urllib.error.HTTPError) as e: self.send(rain=-1)
        self.assertEqual(e.exception.code,400)
    def test_home(self): self.assertIn(b'Weather Alert System',urllib.request.urlopen(self.url).read())
    def test_health(self): self.assertEqual(json.load(urllib.request.urlopen(self.url+'/api/health'))['status'],'ok')
    def test_monitor(self): self.send(); self.assertGreater(json.load(urllib.request.urlopen(self.url+'/api/monitor'))['total'],0)
if __name__=='__main__': unittest.main()
