from flask import Flask, render_template, request, jsonify
import sqlite3, os, math, time
from contextlib import closing

def evaluate(rain, wind):
    rain, wind = float(rain), float(wind)
    if not all(math.isfinite(x) and x >= 0 for x in (rain, wind)):
        raise ValueError('Enter finite non-negative measurements')
    return [name for name, condition in [('FLOOD', rain >= 100), ('STORM', wind >= 75)] if condition]

def delivery_status(seconds):
    return 'ON TIME' if 0 <= seconds < 600 else 'LATE'

def create_app(database=None):
    app = Flask(__name__)
    app.config['DATABASE'] = database or os.getenv('WEATHER_DB', 'weather.db')
    def db():
        conn = sqlite3.connect(app.config['DATABASE']); conn.row_factory = sqlite3.Row
        return conn
    with closing(db()) as c:
        c.execute('CREATE TABLE IF NOT EXISTS alerts (id INTEGER PRIMARY KEY, district TEXT, hazard TEXT, rain REAL, wind REAL, delay REAL, status TEXT, created TEXT DEFAULT CURRENT_TIMESTAMP)'); c.commit()
    @app.get('/')
    def home():
        with closing(db()) as c:
            rows = [dict(r) for r in c.execute('SELECT * FROM alerts ORDER BY id DESC')]
        return render_template('index.html', alerts=rows, late=sum(r['status']=='LATE' for r in rows))
    @app.post('/api/alerts')
    def alerts():
        data = request.get_json(silent=True) or request.form
        try:
            district = str(data['district']).strip()
            if not district or len(district)>100: raise ValueError('Invalid district')
            rain, wind = float(data['rain']), float(data['wind'])
            delay = float(data.get('delay',0))
            if not math.isfinite(delay) or delay<0: raise ValueError('Invalid delay')
            hazards = evaluate(rain, wind)
        except (KeyError, TypeError, ValueError):
            return jsonify(error='Provide district and valid non-negative numeric readings and delay'),400
        with closing(db()) as c:
            for hazard in hazards:
                c.execute('INSERT INTO alerts(district,hazard,rain,wind,delay,status) VALUES(?,?,?,?,?,?)',(district,hazard,rain,wind,delay,delivery_status(delay)))
            c.commit()
        return jsonify(hazards=hazards,status=delivery_status(delay) if hazards else 'SAFE',target_residents=200000,channels=['SMS','APP'],simulated=True)
    @app.get('/api/monitor')
    def monitor():
        with closing(db()) as c:
            rows = c.execute('SELECT delay,status FROM alerts').fetchall()
        return jsonify(total=len(rows),late=sum(r['status']=='LATE' for r in rows),average_delay_seconds=sum(r['delay'] for r in rows)/len(rows) if rows else 0,simulated=True)
    @app.get('/api/health')
    def health(): return jsonify(status='ok')
    return app

if __name__=='__main__': create_app().run(host='0.0.0.0',port=int(os.getenv('PORT',5000)))
