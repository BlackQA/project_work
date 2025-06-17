pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                git branch: 'stage_one',
                url: 'https://github.com/BlackQA/project_work.git'
            }
        }

        stage('Prepare') {
            steps {
                script {
                    sh '''
                    echo "Установка зависимостей Python..."
                    python3 -m venv venv
                    . venv/bin/activate

                    # Добавляем проект в PYTHONPATH
                    export PYTHONPATH="${WORKSPACE}:${PYTHONPATH}"

                    # Устанавливаем зависимости
                    if [ -f "requirements.txt" ]; then
                        pip install -r requirements.txt
                    else
                        pip install pytest allure-pytest
                    fi
                    '''
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    sh '''
                    . venv/bin/activate
                    export PYTHONPATH="${WORKSPACE}:${PYTHONPATH}"
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