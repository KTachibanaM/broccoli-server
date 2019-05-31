pipeline {
    agent none
    stages {
        stage('Test') {
            agent {
                docker {
                    image 'python:3.7.3-stretch'
                }
            }
            steps {
                withEnv(["HOME=/root"]) {
                    sh 'python --version'
                    sh 'pip install pipenv'
                    dir("server") {
                        sh 'pipenv install'
                        sh 'pipenv run python -m unittest discover tests -v'
                    }
                }
            }
            post {
                cleanup {
                    cleanWs()
                }
            }
        }
    }
}