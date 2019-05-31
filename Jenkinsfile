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
                dir("server") {
                    sh 'pip install --user pipenv'
                    sh 'pipenv install'
                    sh 'pipenv run python -m unittest discover tests -v'
                }
            }
        }
    }
}