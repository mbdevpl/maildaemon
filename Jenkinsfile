#!/usr/bin/env groovy

library 'jenkins-mbdev-pl-libs'

pipeline {

  options {
    ansiColor('xterm')
  }

  environment {
    PYTHON_MODULES = 'maildaemon test *.py'
  }

  agent any

  stages {
    stage('Matrix') {
      matrix {

        axes {
          axis {
            name 'PYTHON_VERSION'
            values '3.11'
          }
        }

        agent {
          dockerfile {
            additionalBuildArgs '--build-arg USER_ID=${USER_ID} --build-arg GROUP_ID=${GROUP_ID}' \
              + ' --build-arg AUX_GROUP_IDS="${AUX_GROUP_IDS}" --build-arg TIMEZONE=${TIMEZONE}' \
              + ' --build-arg PYTHON_VERSION=${PYTHON_VERSION}'
            args '--group-add 133 --group-add 997 --group-add 999 --group-add 1001' \
              + ' -v "/var/run/docker.sock:/var/run/docker.sock"'
            label 'docker'
          }
        }

        stages {

          stage('Lint') {
            when {
              environment name: 'PYTHON_VERSION', value: '3.11'
            }
            steps {
              sh """#!/usr/bin/env bash
                set -Eeux
                python -m pylint ${PYTHON_MODULES} |& tee pylint.log
                echo "\${PIPESTATUS[0]}" | tee pylint_status.log
                python -m mypy ${PYTHON_MODULES} |& tee mypy.log
                echo "\${PIPESTATUS[0]}" | tee mypy_status.log
                python -m flake518 ${PYTHON_MODULES} |& tee flake518.log
                echo "\${PIPESTATUS[0]}" | tee flake518_status.log
                python -m pydocstyle ${PYTHON_MODULES} |& tee pydocstyle.log
                echo "\${PIPESTATUS[0]}" | tee pydocstyle_status.log
              """
            }
          }

          stage('Test') {
            steps {
              sh '''#!/usr/bin/env bash
                set -Eeuxo pipefail
                docker run --rm -d --name greenmail --network "container:$HOSTNAME" \
                  -e GREENMAIL_OPTS='-Dgreenmail.verbose -Dgreenmail.setup.test.all -Dgreenmail.hostname=0.0.0.0 -Dgreenmail.users=login:password@domain.com -Dgreenmail.users.login=email -Dgreenmail.auth.disabled' \
                  -t greenmail/standalone:2.0.0
                .build/check_ports.sh
                python -m coverage run --branch --source . -m unittest -v test.test_smtp_connection
                python -m coverage run --append --branch --source . -m unittest -v
              '''
            }
          }

          stage('Coverage') {
            when {
              environment name: 'PYTHON_VERSION', value: '3.11'
            }
            steps {
              sh '''#!/usr/bin/env bash
                set -Eeux
                python -m coverage report --show-missing |& tee coverage.log
                echo "${PIPESTATUS[0]}" | tee coverage_status.log
              '''
              script {
                defaultHandlers.afterPythonBuild()
              }
            }
          }

          stage('Codecov') {
            environment {
              CODECOV_TOKEN = credentials('codecov-token-mbdevpl-maildaemon')
            }
            steps {
              sh '''#!/usr/bin/env bash
                set -Eeuxo pipefail
                python -m codecov --token ${CODECOV_TOKEN}
              '''
            }
          }

        }

      }
    }
  }

  post {
    always {
      sh '''#!/usr/bin/env bash
        set -Eeuxo pipefail
        docker container kill greenmail || echo "Greenmail was not running, continuing"
      '''
    }
    unsuccessful {
      script {
        defaultHandlers.afterBuildFailed()
      }
    }
    regression {
      script {
        defaultHandlers.afterBuildBroken()
      }
    }
    fixed {
      script {
        defaultHandlers.afterBuildFixed()
      }
    }
  }

}
