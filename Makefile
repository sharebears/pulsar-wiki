lint:
	isort -rc .

tests:
	flake8
	mypy --no-strict-optional wiki/
	pytest --cov-report term-missing --cov-branch --cov=wiki tests/

.PHONY: lint tests
