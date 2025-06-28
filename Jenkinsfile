pipeline {
    agent any

    environment {
        DOCKERHUB_CREDENTIALS = credentials('dockerhub')
        IMAGE_NAME = 'hivebox-img'
        IMAGE_TAG = "${BUILD_NUMBER}"
        CONTAINER_NAME = "hivebox"
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
                    venv/bin/python -m pytest test_app.py
                '''
            }
        }

        stage("SonarCloud Analysis") {
            steps {
                withCredentials([string(credentialsId: 'SONAR_TOKEN', variable: 'SONAR_TOKEN')]) {
                    sh '''
                        . venv/bin/activate
                        pip install -U sonar-scanner-cli
                        sonar-scanner \
                        -Dsonar.login=$SONAR_TOKEN
                    '''
                }
            }
        }


        stage("HadolintDocker") {
            steps {
                script {
                    def hadolintResult = sh(script: "hadolint Dockerfile", returnStatus: true)
                    if (hadolintResult == 0) {
                        sh "docker build -t ${IMAGE_NAME}:${BUILD_NUMBER} ."
                        sh "docker rm -f ${CONTAINER_NAME}"
                        sh "docker run -d --name ${CONTAINER_NAME} -p 5000:5000 ${IMAGE_NAME}:${BUILD_NUMBER}"
                    } else {
                        echo "Hadolint found issues in Dockerfile"
                    }
                }
            }
        }

        stage("Integration Testing") {
            steps {
               script {
                    def hivebox_ip = sh(script: "docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' ${CONTAINER_NAME}", returnStdout: true).trim()
                    sh """
                        . venv/bin/activate
                        HIVEBOX_IP=$hivebox_ip pytest test_integration.py
                    """
                }
            }
        }
    }
}