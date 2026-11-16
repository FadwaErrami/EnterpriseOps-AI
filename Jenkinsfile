
pipeline {
    agent any

    environment {
        PYTHON = 'C:\\Users\\hp\\AppData\\Local\\Programs\\Python\\Python311\\python.exe'
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Retrieving EnterpriseOps AI from GitHub'
                checkout scm
            }
        }

        stage('Backend - Tests') {
            steps {
                bat '''
                    "%PYTHON%" --version
                    "%PYTHON%" -m pip install --upgrade pip
                '''

                script {
                    if (fileExists('requirements.txt')) {
                        bat '"%PYTHON%" -m pip install -r requirements.txt'
                    } else if (fileExists('backend/requirements.txt')) {
                        bat '"%PYTHON%" -m pip install -r backend/requirements.txt'
                    } else {
                        error('No requirements.txt found')
                    }
                }

                bat '''
                    "%PYTHON%" -m pip install pytest
                    "%PYTHON%" -m pytest backend -v
                '''
            }
        }

        stage('Frontend - Build') {
            steps {
                withEnv(['PATH+NODE=C:\\Program Files\\nodejs']) {
                    dir('frontend') {
                        bat '''
                            node --version
                            npm --version
                            npm ci
                            npm run build
                        '''
                    }
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
