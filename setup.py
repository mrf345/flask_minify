from setuptools import setup
with open('README.py') as readme:
    ld = readme.read()


setup(
    name='Flask-Minify',
    version='0.4',
    url='https://github.com/mrf345/flask_minify/',
    download_url='https://github.com/mrf345/flask_minify/archive/0.4.tar.gz',
    license='MIT',
    author='Mohamed Feddad',
    author_email='mrf345@gmail.com',
    description='flask extension to minify html, css, js and less',
    long_description=ld,
    py_modules=['minify'],
    packages=['flask_minify'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask',
        'htmlmin',
        'jsmin',
        'lesscpy'
    ],
    keywords=['flask', 'extension', 'minifer', 'htmlmin', 'lesscpy',
              'jsmin', 'html', 'js', 'less', 'css'],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
