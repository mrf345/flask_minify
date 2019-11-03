tests: install
	py.test --cov=./flask_minify tests/*
test: install
	py.test --cov=./flask_minify tests/integration.py::$$u
run: install
	python tests/integration.py
install:
	pip install --quiet -r requirements/dev.txt
