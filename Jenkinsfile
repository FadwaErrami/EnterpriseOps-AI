
pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                echo 'Retrieving EnterpriseOps AI source code'
                checkout scm
            }
        }

        stage('Backend - Tests') {
            steps {
                bat '''
                    python --version
                    python -m pip install -r requirements.txt
                    python -m pytest backend -v
                '''
            }
        }

        stage('Frontend - Build') {
            steps {
                dir('frontend') {
                    bat '''
                        node --version
                        npm ci
                        npm run build
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'EnterpriseOps AI CI Pipeline: SUCCESS'
        }
        failure {
            echo 'EnterpriseOps AI CI Pipeline: FAILURE'
        }
    }
}
