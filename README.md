# Weather Alert System — Case 35
Academic prototype using Flask, SQLite, V-Model and Kanban. SMS/app delivery and delays are simulated; 200,000 is a target, not a tested capacity. Thresholds (100 mm rainfall, 75 km/h wind) are demonstration assumptions, not official warning criteria. Local demo only; no authentication or live weather feed.

## Windows VS Code PowerShell
Extract ZIP and open Weather_Alert_System folder. Run:
```
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```
Open http://127.0.0.1:5000. In a second terminal:
```
.\.venv\Scripts\python.exe -m pytest -v
.\.venv\Scripts\python.exe -m pytest --cov=app --cov-report=html --cov-report=xml
```
Open htmlcov/index.html for coverage. For Selenium, install Chrome, keep server running, and run:
```
.\.venv\Scripts\python.exe selenium_demo.py
```
Chrome driver may require internet access. Screenshot saved in evidence/selenium.png on success.

Docker (optional): `docker build -t weather-alert .` then `docker run --rm -p 5000:5000 weather-alert`.
Jenkinsfile assumes a Linux agent with Python and Docker. SonarQube configuration requires a separately configured scanner/server. No credentials included.

## Evidence
27 parametrized pytest cases are supplied. Execution here was blocked by missing Flask and unavailable package network; run locally to obtain actual results. Selenium, Docker and Jenkins have not been executed here. Manual tests are in docs/test-plan.md.

## Offline mode (no pip required)
Run `python run_offline.py` and open http://127.0.0.1:5000. Stop with Ctrl+C. Run `python -m unittest -v test_offline` for offline tests. Offline mode uses its own SQLite database.
