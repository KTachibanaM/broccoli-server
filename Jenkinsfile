pipeline {
    agent none
    stages {
        stage('Test') {
            agent {
                docker {
                    image 'kennethreitz/pipenv:latest'
                }
            }
            steps {
                dir("server") {
                    sh 'pipenv install'
                    sh 'pipenv run python -m unittest discover tests -v'
                }
            }
        }
    }
}