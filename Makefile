tests: install
	py.test --cov=./flask_minify tests/*
test: install
	py.test --cov=./flask_minify tests/integration.py::$$u
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
