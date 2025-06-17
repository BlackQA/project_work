pipeline {
    agent any

    environment {
        OPENCART_URL = "http://opencart:8080"
    }

    stages {
        stage('Prepare') {
            steps {
                script {
                    sh '''
                    apt-get update && apt-get install -y python3 python3-pip python3-venv
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install -r requirements.txt
                    pip install pytest allure-pytest
                    '''
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    sh '''
                    . venv/bin/activate
                    pytest --alluredir=allure-results ./tests
                    '''
                }
            }
        }

        stage('Generate Report') {
            steps {
                allure([
                    includeProperties: false,
                    jdk: '',
                    properties: [],
                    reportBuildPolicy: 'ALWAYS',
                    results: [[path: 'allure-results']]
                ])
            }
        }
    }
}