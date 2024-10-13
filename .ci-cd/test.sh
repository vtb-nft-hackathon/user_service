#!/bin/sh

docker compose run --rm api pytest -v tests/ --junitxml tests-unit-results.xml --cov=app --cov-report='xml:coverage-tests-unit.xml'
tests_result=$?

docker compose down -v --remove-orphans --rmi all

if [ $tests_result != 0 ]; then
  echo "unit tests finished with fail"
  exit $tests_result
fi
