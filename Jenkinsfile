
pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
        timestamps()
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    environment {
        PYTHONUNBUFFERED = '1'
        PIP_DISABLE_PIP_VERSION_CHECK = '1'
    }

    stages {

        stage('1. Checkout') {
            steps {
                echo 'Checking out source code from GitHub'
                checkout scm
            }
        }


stage('2. Environment Setup') {
    steps {
        echo 'Checking required tools'

        bat '''
            "C:\\Users\\hp\\AppData\\Local\\Programs\\Python\\Python311\\python.exe" --version
            if errorlevel 1 exit /b 1

            node --version
            if errorlevel 1 exit /b 1

            npm --version
            if errorlevel 1 exit /b 1

            git --version
            if errorlevel 1 exit /b 1
        '''

        echo 'Creating isolated Python environment'

        bat '''
            "C:\\Users\\hp\\AppData\\Local\\Programs\\Python\\Python311\\python.exe" -m venv .venv
            if errorlevel 1 exit /b 1

            .venv\\Scripts\\python.exe --version
            if errorlevel 1 exit /b 1

            .venv\\Scripts\\python.exe -m pip install --upgrade pip
            if errorlevel 1 exit /b 1
        '''
    }
}

        stage('3. Backend - Dependencies') {
            steps {
                script {
                    if (!fileExists('requirements.txt')) {
                        error('requirements.txt not found in project root')
                    }
                }

                bat '''
                    .venv\\Scripts\\python.exe -m pip install -r requirements.txt
                '''
            }
        }

        stage('4. Backend - Automated Tests') {
            steps {
                bat '''
                    if not exist reports mkdir reports

                    .venv\\Scripts\\python.exe -m pytest backend/tests -v --junitxml=reports/pytest-results.xml
                '''
            }

            post {
                always {
                    junit(
                        testResults: 'reports/pytest-results.xml',
                        allowEmptyResults: true
                    )
                }
            }
        }

        stage('5. Frontend - Dependencies') {
            steps {
                script {
                    if (!fileExists('frontend/package.json')) {
                        error('Frontend package.json not found')
                    }

                    if (!fileExists('frontend/package-lock.json')) {
                        error('package-lock.json is required for reproducible npm ci installation')
                    }
                }

                dir('frontend') {
                    bat 'npm ci'
                }
            }
        }

        stage('6. Frontend - Production Build') {
            steps {
                dir('frontend') {
                    bat 'npm run build'
                }

                script {
                    if (!fileExists('frontend/dist/index.html')) {
                        error('Frontend production build failed: dist/index.html not found')
                    }
                }
            }
        }

    }

    post {

        success {
            echo '''
            ============================================
                  ENTERPRISEOPS AI - CI SUCCESS
            ============================================
            GitHub checkout:       SUCCESS
            Python environment:    SUCCESS
            Backend dependencies:  SUCCESS
            Backend tests:         SUCCESS
            Frontend installation: SUCCESS
            Frontend build:        SUCCESS
            ============================================
            '''
        }

        failure {
            echo '''
            ============================================
                  ENTERPRISEOPS AI - CI FAILURE
            ============================================
            One or more pipeline stages failed.
            Check the Jenkins Console Output.
            ============================================
            '''
        }

        always {
            archiveArtifacts(
                artifacts: 'frontend/dist/**,reports/**',
                allowEmptyArchive: true,
                fingerprint: true
            )

            echo 'Pipeline execution completed.'
        }
    }
}
