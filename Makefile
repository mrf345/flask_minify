SHELL := /bin/bash

# repeats the tests a given number of times
c ?= 1 

test: install
	test -f .venv/bin/activate && source .venv/bin/activate && python -m bandit -c bandit.yml -r . && python -m pytest --count=$(c)
lint: install
	source .venv/bin/activate && python -m isort -sg "**/.venv*" --profile black --check . && python -m black --check .
format: install
	test -f .venv/bin/activate && source .venv/bin/activate && python -m isort -sg "**/.venv*" --profile black . && python -m black .
run: install
	python tests/integration.py
release: install-dev clean
	test -f .venv/bin/activate && source .venv/bin/activate &&  python setup.py sdist bdist_wheel && python -m twine upload dist/*
	$(MAKE) clean
clean:
	rm -rf dist build Flask_Minify.egg-info .eggs
install:
	test -f .venv/bin/activate && source .venv/bin/activate && pip install --quiet -r requirements/test.txt
install-dev:
	test -f .venv/bin/activate && source .venv/bin/activate && pip install --quiet -r requirements/dev.txt
