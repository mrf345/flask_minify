from os import path
from setuptools import setup


basedir = path.abspath(path.dirname(__file__))
long_description = ''
requirements = []
test_requirements = []
requirements_path = path.join(basedir, 'requirements')


with open(path.join(basedir, path.join('flask_minify', 'about.py'))) as f:
    exec(f.read())

with open(path.join(basedir, 'README.md')) as f:
    long_description += f.read()

with open(path.join(requirements_path, 'main.txt')) as f:
    requirements += [line for line in f.read().split('\n') if line]
    test_requirements += requirements

with open(path.join(requirements_path, 'test.txt')) as f:
    test_requirements += [
        line for line in f.read().split('\n')
        if line and not line.startswith('-r')]


setup(
    name='Flask-Minify',
    version=__version__,  # noqa
    url='https://github.com/mrf345/flask_minify/',
    download_url='https://github.com/mrf345/flask_minify/archive/%s.tar.gz'
    % __version__,  # noqa
    license=__license__,  # noqa
    author=__author__,  # noqa
    author_email=__email__,  # noqa
    description=__doc__,  # noqa
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=['flask_minify'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=requirements,
    setup_requires=test_requirements,
    keywords=['flask', 'extension', 'minifer', 'htmlmin', 'lesscpy',
              'jsmin', 'html', 'js', 'less', 'css'],
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
