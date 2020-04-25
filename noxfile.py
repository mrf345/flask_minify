import nox

SUPPORTED_VERSIONS = ['2.7', '3.4', '3.5', '3.6', '3.7', '3.8']


@nox.session(python=SUPPORTED_VERSIONS)
def lint(s):
    s.install('flake8')
    s.run('flake8', 'flask_minify')


@nox.session(python=SUPPORTED_VERSIONS)
def test(s):
    s.install('-r', './requirements/test.txt')
    s.run('py.test',
          '--cov=./flask_minify',
          './tests/integration.py',
          './tests/units.py')
