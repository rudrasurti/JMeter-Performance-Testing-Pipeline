pipeline {
    agent any
    parameters {
        string(name: 'USERS', defaultValue: '10', description: 'Virtual users')
        string(name: 'LOOPS', defaultValue: '5', description: 'Loops per user')
    }
    environment {
        JMETER_VERSION = '5.6.3'
        MAX_ERROR_PCT = '2'
        MAX_P95_MS = '5000'
    }
    triggers { cron('H 5 * * 1') }
    stages {
        stage('Get JMeter') {
            steps {
                sh '''
                  [ -d apache-jmeter-$JMETER_VERSION ] || \
                  curl -fsSL https://archive.apache.org/dist/jmeter/binaries/apache-jmeter-$JMETER_VERSION.tgz | tar xz
                '''
            }
        }
        stage('Load test') {
            steps {
                sh '''
                  rm -rf results && mkdir results
                  apache-jmeter-$JMETER_VERSION/bin/jmeter -n -t perf/booking-load.jmx \
                    -Jusers=$USERS -Jloops=$LOOPS \
                    -Jjmeter.save.saveservice.output_format=csv \
                    -l results/results.jtl -e -o results/dashboard
                '''
            }
        }
        stage('Check limits') {
            steps { sh 'python3 scripts/check_thresholds.py results/results.jtl' }
        }
    }
    post {
        always {
            archiveArtifacts artifacts: 'results/**', allowEmptyArchive: true
            publishHTML(target: [reportDir: 'results/dashboard', reportFiles: 'index.html', reportName: 'JMeter Dashboard', keepAll: true, alwaysLinkToLastBuild: true, allowMissing: true])
        }
    }
}
