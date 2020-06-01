from os import path
from setuptools import setup


basedir = path.abspath(path.dirname(__file__))
long_description = ''
requirements = []
test_requirements = []


with open(path.join(basedir, path.join('flask_minify', 'about.py'))) as f:
    exec(f.read())

with open(path.join(basedir, 'README.md')) as f:
    long_description += f.read()

with open(path.join(basedir, 'requirements/main.txt')) as f:
    requirements += [l for l in f.read().split('\n') if l]
    test_requirements += requirements

with open(path.join(basedir, 'requirements/test.txt')) as f:
    test_requirements += [l for l in f.read().split('\n') if l and not l.startswith('-r')]


setup(
    name='Flask-Minify',
    version=__version__,
    url='https://github.com/mrf345/flask_minify/',
    download_url='https://github.com/mrf345/flask_minify/archive/%s.tar.gz'
    % __version__,
    license=__license__,
    author=__author__,
    author_email=__email__,
    description=__doc__,
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
        'Programming Language :: Python :: 3.4',
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
