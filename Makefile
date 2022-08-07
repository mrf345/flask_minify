test: install
	python -m bandit -c bandit.yml -r . && python -m pytest
lint: install
	python -m isort --profile black --check . && python -m black --check .
format: install
	python -m isort --profile black .
	python -m black .
run: install
	python tests/integration.py
release: install-dev clean
	python setup.py sdist bdist_wheel
	python -m twine upload dist/*
	$(MAKE) clean
clean:
	rm -rf dist build Flask_Minify.egg-info .eggs
install:
	test -f .venv/bin/activate && source .venv/bin/activate
	pip install --quiet -r requirements/test.txt
install-dev:
	test -f .venv/bin/activate && source .venv/bin/activate
	pip install --quiet -r requirements/dev.txt
