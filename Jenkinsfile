pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                echo 'Building..'
                sh 'virtualenv-2.7 .; bin/pip install -r requirements.txt'
            }
        }
        stage('Test') {
            steps {
                sh'bin/pytest zopyx.smashdocs'
        }
    }
}

