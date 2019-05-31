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
                withEnv(["HOME=${env.WORKSPACE}"]) {
                    sh 'python --version'
                    sh 'pip install --user pipenv'
                    dir("server") {
                        sh '$HOME/.local/bin/pipenv install'
                        sh '$HOME/.local/bin/pipenv run python -m unittest discover tests -v'
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