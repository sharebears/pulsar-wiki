lint:
	isort -rc .
_tests:
	flake8
	mypy --no-strict-optional forums/
	pytest --cov-report term-missing --cov-branch --cov=forums tests/
tests: _tests
