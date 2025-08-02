pipeline {
    agent any

    environment {
        DOCKERHUB_CREDENTIALS = credentials('dockerhub')
        IMAGE_NAME = 'hivebox-img'
        IMAGE_TAG = "${BUILD_NUMBER}"
        CONTAINER_NAME = "hivebox"
        GIT_REPO = 'https://github.com/Khaled1771/HiveBox.git'
        BRANCH = 'Testing'
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

        stage("Hadolint Docker") {
            steps {
                script {
                    def hadolintResult = sh(script: "hadolint Dockerfile", returnStatus: true)
                    if (hadolintResult == 0) {
                        sh "docker build -t ${IMAGE_NAME}:${BUILD_NUMBER} ."
                        /*  <<<<    Play with Docker containers    >>>>
                        sh "docker rm -f ${CONTAINER_NAME}"
                        // Get MinIO'IP address for HiveBox app 
                        def minioIp = sh(script: "docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' minio", returnStdout: true).trim()
                        // // Get Redis-valkey'IP address for HiveBox app 
                        def valkeyIp = sh(script: "docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' valkey-hivebox", returnStdout: true).trim()
                        // Run HiveBox Container with a specific env vars.
                        sh "docker run -d --name ${CONTAINER_NAME} -p 5000:5000 -e MINIO_ENDPOINT=${minioIp} -e REDIS_HOST=${valkeyIp} ${IMAGE_NAME}:${BUILD_NUMBER}"
                        */
                    } else {
                        error "Hadolint found issues in Dockerfile. Failing the pipeline."
                    }
                }
            }
        }

        stage("Ansible & Kubernetes") {
            steps {
                script {
                    def hivebox_image_id = sh(script: "docker exec kind-control-plane crictl images | grep hivebox-img | awk '{print \$3}'", returnStdout: true).trim()    // Show the image's ID to delete it
                    sh "ansible-playbook Ansible/Update-Kubernetes.yaml --extra-vars 'oldImageID=$hivebox_image_id image_name=${IMAGE_NAME} image_tag=${IMAGE_TAG} manifest_file=/mnt/MyData/Courses/Projects/HiveBox/Hivebox-chart/values.yaml'"     // Enjoy with automation using Ansible 
                }
            }
        }

        stage("Helm Upgrade") {
            steps {
                script {
                    withCredentials([file(credentialsId: 'kubeconfig-hivebox', variable: 'KUBECONFIG')]) {
                        sh '''
                            helm upgrade --install hivebox-release /mnt/MyData/Courses/Projects/HiveBox/Hivebox-chart --kubeconfig $KUBECONFIG --namespace testing
                        '''
                    }
                }
            }
        }

        stage("Sleep before Analysis") {
            steps {
                echo "Sleeping for 60 seconds..."
                sleep time: 60, unit: 'SECONDS'
            }
        }
                    // curl -sSLo sonar-scanner.zip https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-5.0.1.3006-linux.zip
                    // unzip -q sonar-scanner.zip            
                    // sh "export PATH=/sonar-scanner-5.0.1.3006-linux/bin:$PATH"
                    // sh "sonar-scanner -Dsonar.login=$SONAR_TOKEN"
        // stage("SonarCloud Analysis") {
        //     steps {
        //         withCredentials([
        //             file(credentialsId: 'kubeconfig-hivebox', variable: 'KUBECONFIG'),
        //             string(credentialsId: 'SONAR_TOKEN', variable: 'SONAR_TOKEN')
        //         ]) {
        //             script {
        //                 def pod_name = sh(script: "kubectl get pods -n testing -l app=flask-app -o jsonpath='{.items[0].metadata.name}' --kubeconfig $KUBECONFIG", returnStdout: true).trim()
        //                 sh "kubectl cp /opt/sonar-scanner-5.0.1.3006-linux $pod_name:/opt/ -n testing --kubeconfig $KUBECONFIG"     // Copy Sonar-Scanner tool -> HiveBox Pod
        //                 sh """
        //                 kubectl exec -i $pod_name -n testing --kubeconfig $KUBECONFIG -- /bin/sh -c '
        //                     export SONAR_TOKEN=${SONAR_TOKEN} && \
        //                     . venv/bin/activate && \
        //                     pytest --cov=. --cov-report=xml && \
        //                     /opt/sonar-scanner-5.0.1.3006-linux/bin/sonar-scanner -Dsonar.login=\$SONAR_TOKEN
        //                 '
        //                 """
        //             }
        //         }
        //     }
        // }


        stage("Unit Testing") {
            steps {
                withCredentials([file(credentialsId: 'kubeconfig-hivebox', variable: 'KUBECONFIG')]) {
                    script {
                        def pod_name = sh(script: "kubectl get pods -n testing -l app=flask-app -o jsonpath='{.items[0].metadata.name}' --kubeconfig $KUBECONFIG", returnStdout: true).trim()
                        sh """
                        kubectl exec -i $pod_name -n testing --kubeconfig $KUBECONFIG -- /bin/sh -c '
                            . venv/bin/activate && \
                            pytest test_app.py
                        '
                        """
                    }
                }
            }
        }

        stage("Integration Testing") {
            steps {
        withCredentials([file(credentialsId: 'kubeconfig-hivebox', variable: 'KUBECONFIG')]) {
            script {
                def pod_name = sh(script: "kubectl get pods -n testing -l app=flask-app -o jsonpath='{.items[0].metadata.name}' --kubeconfig $KUBECONFIG", returnStdout: true).trim()

                // Readiness inside the Pod, Waiting 10 Sec.
                sh """
                    echo "Waiting for pod to be ready..."
                    kubectl wait --for=condition=ready pod/$pod_name -n testing --timeout=5s --kubeconfig $KUBECONFIG

                    kubectl exec -i $pod_name --kubeconfig $KUBECONFIG -- /bin/sh -c '
                        . venv/bin/activate && \
                        pytest test_integration.py
                    '
                """
            }
        }
    }
            //    script {
            //         /* <<<<    Integration Testing with Docker containers    >>>>
            //         def hivebox_ip = sh(script: "docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' ${CONTAINER_NAME}", returnStdout: true).trim()
            //         sh """
            //             . venv/bin/activate
            //             HIVEBOX_IP=$hivebox_ip pytest test_integration.py
            //         """
            //         */
            //     }
        }

        stage("E2E Testing") {
            steps {
                withCredentials([file(credentialsId: 'kubeconfig-hivebox', variable: 'KUBECONFIG')]) {
                    script {
                        def pod_name = sh(script: "kubectl get pods -n testing -l app=flask-app -o jsonpath='{.items[0].metadata.name}' --kubeconfig $KUBECONFIG", returnStdout: true).trim()
                        sh """
                        kubectl exec -i $pod_name -n testing --kubeconfig $KUBECONFIG -- /bin/sh -c '
                            . venv/bin/activate && \
                            pytest test_e2e.py -v
                        '
                        """
                    }
                }
            }
                    /* <<<<    E2E Testing with Docker containers    >>>>
                    def hivebox_ip = sh(script: "docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' ${CONTAINER_NAME}", returnStdout: true).trim()
                    sh """
                        . venv/bin/activate
                        HIVEBOX_IP=$hivebox_ip pytest test_e2e.py -v
                    """
                    */
                    // Kuberntes Deployment via Helm
            
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