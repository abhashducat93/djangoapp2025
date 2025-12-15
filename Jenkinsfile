pipeline {
    agent any
    
    environment {
        APP_NAME = 'enhanced-django-app'
        DOCKER_REGISTRY = 'your-registry'  // Set your registry
        DOCKER_IMAGE = "${DOCKER_REGISTRY}/${APP_NAME}:${BUILD_NUMBER}"
        DOCKER_IMAGE_LATEST = "${DOCKER_REGISTRY}/${APP_NAME}:latest"
    }
    
    options {
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
        disableConcurrentBuilds()
    }
    
    triggers {
        pollSCM('H/5 * * * *')  // Poll every 5 minutes
        // Uncomment for GitHub webhook
        // githubPush()
    }
    
    stages {
        stage('Checkout & Initialize') {
            steps {
                checkout scm
                sh '''
                    echo "📦 Building ${APP_NAME}"
                    echo "Branch: ${BRANCH_NAME}"
                    echo "Build Number: ${BUILD_NUMBER}"
                    echo "Workspace: ${WORKSPACE}"
                '''
            }
        }
        
        stage('Setup Python Environment') {
            steps {
                sh '''
                    echo "🐍 Setting up Python environment..."
                    python -m venv venv || true
                    source venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }
        
        stage('Run Django Checks') {
            steps {
                sh '''
                    echo "🔍 Running Django system checks..."
                    source venv/bin/activate
                    python manage.py check --deploy
                    python manage.py makemigrations --check --dry-run
                '''
            }
        }
        
        stage('Run Tests') {
            steps {
                sh '''
                    echo "🧪 Running Django tests..."
                    source venv/bin/activate
                    python manage.py test --verbosity=2
                '''
            }
            post {
                success {
                    echo '✅ All tests passed!'
                }
                failure {
                    echo '❌ Tests failed!'
                }
            }
        }
        
        stage('Security Scan') {
            steps {
                sh '''
                    echo "🛡️ Running security checks..."
                    source venv/bin/activate
                    pip install bandit safety
                    bandit -r . -f json -o bandit-report.json || true
                    safety check --json --output safety-report.json || true
                '''
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    echo "🐳 Building Docker image: ${DOCKER_IMAGE}"
                    sh "docker build -t ${DOCKER_IMAGE} -t ${DOCKER_IMAGE_LATEST} ."
                }
            }
        }
        
        stage('Scan Docker Image') {
            steps {
                sh '''
                    echo "🔍 Scanning Docker image for vulnerabilities..."
                    docker scan ${DOCKER_IMAGE} --json || true
                '''
            }
        }
        
        stage('Push to Registry') {
            when {
                expression { 
                    env.BRANCH_NAME == 'main' || env.BRANCH_NAME == 'master' 
                }
            }
            steps {
                script {
                    echo "📤 Pushing Docker image to registry..."
                    // Uncomment and configure if you have a registry
                    // docker.withRegistry('https://your-registry', 'docker-credentials') {
                    //     sh "docker push ${DOCKER_IMAGE}"
                    //     sh "docker push ${DOCKER_IMAGE_LATEST}"
                    // }
                    echo "📦 Image ready: ${DOCKER_IMAGE}"
                }
            }
        }
        
        stage('Deploy to Environment') {
            when {
                expression { 
                    env.BRANCH_NAME == 'main' || env.BRANCH_NAME == 'master' 
                }
            }
            steps {
                sh '''
                    echo " 🚀 Deploying application..."
                    
                    # Stop and remove existing container
                    docker stop ${APP_NAME} 2>/dev/null || true
                    docker rm ${APP_NAME} 2>/dev/null || true
                    
                    # Run new container with production settings
                    docker run -d \
                        --name ${APP_NAME} \
                        -p 8000:8000 \
                        -e DEBUG=False \
                        -e SECRET_KEY=${SECRET_KEY:-default-secret-key} \
                        -v ${APP_NAME}_static:/app/staticfiles \
                        -v ${APP_NAME}_media:/app/media \
                        --restart unless-stopped \
                        ${DOCKER_IMAGE_LATEST}
                    
                    echo "✅ Application deployed successfully!"
                '''
            }
        }
        
        stage('Health Check & Validation') {
            steps {
                retry(3) {
                    sh '''
                        echo "🏥 Performing health checks..."
                        sleep 10
                        
                        # Check container status
                        CONTAINER_STATUS=$(docker inspect -f '{{.State.Status}}' ${APP_NAME})
                        echo "Container Status: ${CONTAINER_STATUS}"
                        
                        if [ "${CONTAINER_STATUS}" != "running" ]; then
                            echo "❌ Container is not running!"
                            exit 1
                        fi
                        
                        # Health endpoint check
                        HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health/)
                        if [ "${HEALTH_RESPONSE}" != "200" ]; then
                            echo "❌ Health check failed with status: ${HEALTH_RESPONSE}"
                            exit 1
                        fi
                        
                        # Main endpoint check
                        MAIN_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/)
                        if [ "${MAIN_RESPONSE}" != "200" ]; then
                            echo "❌ Main endpoint failed with status: ${MAIN_RESPONSE}"
                            exit 1
                        fi
                        
                        # API endpoint check
                        API_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/status/)
                        if [ "${API_RESPONSE}" != "200" ]; then
                            echo "❌ API endpoint failed with status: ${API_RESPONSE}"
                            exit 1
                        fi
                        
                        echo "✅ All health checks passed!"
                    '''
                }
            }
        }
        
        stage('Performance Test') {
            steps {
                sh '''
                    echo "⚡ Running quick performance test..."
                    # Install Apache Bench if not present
                    which ab || apt-get update && apt-get install -y apache2-utils
                    
                    # Run benchmark
                    ab -n 100 -c 10 http://localhost:8000/health/ | grep "Time per request" || true
                '''
            }
        }
    }
    
    post {
        always {
            echo "🧹 Cleaning up workspace..."
            cleanWs()
            
            // Archive test reports
            junit '**/test-reports/*.xml'
            archiveArtifacts artifacts: '**/reports/*.json', allowEmptyArchive: true
            
            // Clean up Docker
            sh '''
                docker system prune -f || true
                docker volume prune -f || true
            '''
        }
        
        success {
            echo "🎉 SUCCESS: Deployment completed!"
            echo "🌐 Application URL: http://localhost:8000"
            echo "🏥 Health Check: http://localhost:8000/health/"
            echo "📊 Dashboard: http://localhost:8000/dashboard/"
            
            // Optional: Send notification
            // emailext (
            //     subject: "SUCCESS: ${APP_NAME} Build #${BUILD_NUMBER}",
            //     body: "Build ${BUILD_NUMBER} completed successfully!\n\nApplication is running at http://your-server:8000",
            //     to: 'team@example.com'
            // )
        }
        
        failure {
            echo "💥 FAILURE: Pipeline failed!"
            
            // Get logs from failed container
            sh '''
                echo "📋 Container logs:"
                docker logs ${APP_NAME} --tail 50 || true
            '''
            
            // Optional: Send failure notification
            // emailext (
            //     subject: "FAILURE: ${APP_NAME} Build #${BUILD_NUMBER}",
            //     body: "Build ${BUILD_NUMBER} failed. Check Jenkins for details.",
            //     to: 'devops@example.com'
            // )
        }
        
        unstable {
            echo "⚠️  UNSTABLE: Some tests failed but pipeline continued"
        }
        
        changed {
            echo "📈 Pipeline status changed"
        }
    }
}