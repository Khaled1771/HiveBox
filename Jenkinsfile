pipeline {
    agent any

    environment {
        DOCKERHUB_CREDENTIALS = credentials('dockerhub')
        IMAGE_NAME = 'hivebox-img'
        IMAGE_TAG = "${BUILD_NUMBER}"
        GIT_REPO = 'https://github.com/Khaled1771/HiveBox.git'
        BRANCH = 'main'
    }

    stages {
        stage("Fetch git repo") {
            steps {
                git branch: "${BRANCH}", url: "${GIT_REPO}"
            }   
        }


        stage('Setup Python venv') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage("Lint Python") {
            steps {
                sh '''
                    venv/bin/pylint main.py test_app.py || true
                '''
            }
        }

        stage("Unit Testing") {
            steps {
                sh '''
                    venv/bin/python -m pytest
                '''
            }
        }

         stage("Hadolint & Docker") {
            steps {
                sh "hadolint Dockerfile"
                def hadolintFlag = $(echo $?)
                if (hadolintFlag == 0) {
                    sh "docker build -t ${IMAGE_NAME}:${BUILD_NUMBER} ."
                }     
            }
        }
    }
}