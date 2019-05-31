pipeline {
    agent {
        docker {
            image 'python:3.7.3-stretch'
        }
    }
    stages {
        stage('Test') {
            steps {
                sh 'pip install --user pipenv'
                dir("server") {
                    sh 'pipenv install'
                    sh 'pipenv run python -m unittest discover tests -v'
                }
            }
        }
    }
}