pipeline {
    agent any

    environment {
        IMAGE_NAME = "aceest-fitness-gym"
        VENV_DIR = "venv"
    }

    options {
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Set Up Environment') {
            steps {
                sh '''
                    python3 -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements-dev.txt
                '''
            }
        }

        stage('Lint & Syntax Check') {
            steps {
                sh '''
                    . ${VENV_DIR}/bin/activate
                    python -m py_compile app.py
                    flake8 app.py tests/ --max-line-length=100
                '''
            }
        }

        stage('Unit Tests') {
            steps {
                sh '''
                    . ${VENV_DIR}/bin/activate
                    pytest -v --junitxml=pytest-results.xml
                '''
            }
            post {
                always {
                    junit 'pytest-results.xml'
                }
            }
        }

        stage('Docker Build') {
            steps {
                sh 'docker build --target final -t ${IMAGE_NAME}:${BUILD_NUMBER} .'
            }
        }
    }

    post {
        success {
            echo 'BUILD phase completed successfully.'
        }
        failure {
            echo 'BUILD phase failed. See console output above for details.'
        }
        cleanup {
            sh 'rm -rf ${VENV_DIR}'
        }
    }
}
