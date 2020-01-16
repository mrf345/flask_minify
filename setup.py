from setuptools import setup
from os import path

from flask_minify import __version__ as VERSION
from flask_minify import __doc__ as DOC


with open(path.join(path.abspath(path.dirname(__file__)), 'README.md'),
          encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='Flask-Minify',
    version=VERSION,
    url='https://github.com/mrf345/flask_minify/',
    download_url='https://github.com/mrf345/flask_minify/archive/%s.tar.gz'
    % VERSION,
    license='MIT',
    author='Mohamed Feddad',
    author_email='mrf345@gmail.com',
    description=DOC,
    long_description=long_description,
    long_description_content_type='text/markdown',
    py_modules=['minify'],
    packages=['flask_minify'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask',
        'htmlmin',
        'jsmin',
        'lesscpy',
        'xxhash'
    ],
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
    ],
    setup_requires=['pytest-runner']
)
