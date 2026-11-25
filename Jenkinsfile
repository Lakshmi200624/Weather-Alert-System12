pipeline {
 agent any
 stages {
  stage('Build') { steps { sh 'python3 -m venv .venv && .venv/bin/pip install -r requirements.txt' } }
  stage('Test') { steps { sh '.venv/bin/python -m pytest --junitxml=results.xml --cov=app --cov-report=xml --cov-report=html' } }
  stage('Package') { steps { sh 'docker build -t weather-alert .' } }
 }
 post { always { junit allowEmptyResults: true, testResults: 'results.xml'; archiveArtifacts artifacts: 'htmlcov/**', allowEmptyArchive: true } }
}
