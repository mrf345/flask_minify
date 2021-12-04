test: install
	pytest
lint: install
	isort --profile black --check .
	black --check .
format: install
	isort --profile black .
	black .
run: install
	python tests/integration.py
release: install clean
	python setup.py sdist bdist_wheel
	python -m twine upload dist/*
	$(MAKE) clean
clean:
	rm -rf dist build Flask_Minify.egg-info .eggs
install:
	pip install --quiet -r requirements/dev.txt
