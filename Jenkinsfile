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

        stage("Hadolint Docker") {
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

        // stage("SonarCloud Analysis") {
        //     steps {
        //         withCredentials([string(credentialsId: 'SONAR_TOKEN', variable: 'SONAR_TOKEN')]) {
                    
        //                 // curl -sSLo sonar-scanner.zip https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-5.0.1.3006-linux.zip
        //                 // unzip -q sonar-scanner.zip
                                    
        //             // sh "export PATH=/sonar-scanner-5.0.1.3006-linux/bin:$PATH"
        //             // sh "sonar-scanner -Dsonar.login=$SONAR_TOKEN"
        //             sh "venv/bin/python -m pytest --cov=. --cov-report=xml"      // Quality Gate in process, need integration tests
        //             sh "/opt/sonar-scanner-5.0.1.3006-linux/bin/sonar-scanner -Dsonar.login=$SONAR_TOKEN"
        //         }
        //     }
        // }

        stage("Ansible & Kubernetes") {
            steps {
                script {
                    def hivebox_image_id = sh(script: "docker exec kind-control-plane crictl images | grep hivebox-img | awk '{print \$3}'", returnStdout: true).trim()    // Show the image's ID to delete it
                    sh "ansible-playbook Ansible/Update-Kubernetes.yaml --extra-vars 'oldImageID=$hivebox_image_id image_name=${IMAGE_NAME} image_tag=${IMAGE_TAG} manifest_file=/mnt/MyData/Courses/Projects/HiveBox/Kubernetes/Flask-Deloyment.yaml'"     // Enjoy with automation using Ansible 
                }
            }
        }

        stage("GitOps with ArgoCD") {
            steps {
              withCredentials([usernamePassword(credentialsId: 'Github', usernameVariable: 'GIT_USERNAME', passwordVariable: 'GIT_PASSWORD')]) {
                    sh """
                        GIT_USERNAME=${GIT_USERNAME} GIT_PASSWORD=${GIT_PASSWORD} \\
                        bash /mnt/MyData/Courses/Projects/HiveBox/GitOps.sh ${BUILD_NUMBER}
                    """
                }
            }
        }
    }
}