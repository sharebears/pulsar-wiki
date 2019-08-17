lint:
	isort -rc .
	black -S -t py37 -l 79 .

tests:
	flake8
	mypy --no-strict-optional wiki/
	pytest --cov-report term-missing --cov-branch --cov=wiki tests/

.PHONY: lint tests
