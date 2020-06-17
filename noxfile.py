import nox

SUPPORTED_VERSIONS = ['2.7', '3.5', '3.6', '3.7', '3.8']


@nox.session(python=SUPPORTED_VERSIONS)
def lint(s):
    s.install('flake8')
    s.run('flake8')


@nox.session(python=SUPPORTED_VERSIONS)
def test(s):
    s.install('-r', './requirements/test.txt')
    s.run('pytest')
