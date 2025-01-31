from os import path

from setuptools import setup

optional_requirements = {"go": 'tdewolff-minify>=2.20.34; platform_system == "Linux"'}
basedir = path.abspath(path.dirname(__file__))
long_description = ""
requirements = []
test_requirements = []
requirements_path = path.join(basedir, "requirements")


with open(path.join(basedir, path.join("flask_minify", "about.py"))) as f:
    exec(f.read())  # nosec

with open(path.join(basedir, "README.md")) as f:
    long_description += f.read()


if path.isdir(requirements_path):
    with open(path.join(requirements_path, "main.txt")) as f:
        requirements += [
            line for line in f.read().split("\n") if line and "[go]" not in line
        ]
        test_requirements += requirements

    with open(path.join(requirements_path, "test.txt")) as f:
        test_requirements += [
            line for line in f.read().split("\n") if line and not line.startswith("-r")
        ]
else:
    requires_path = path.join(
        path.join(basedir, "Flask_Minify.egg-info"), "requires.txt"
    )

    with open(requires_path) as f:
        requirements += [line for line in f.read().split("\n") if line]

supported_python_classifiers = [
    "Programming Language :: Python :: {0}".format(v) for v in __supported_versions__
]

setup(
    name="Flask-Minify",
    version=__version__,
    url="https://github.com/mrf345/flask_minify/",
    download_url="https://github.com/mrf345/flask_minify/archive/%s.tar.gz"
    % __version__,
    license=__license__,
    author=__author__,
    author_email=__email__,
    description=__doc__,
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=["flask_minify"],
    zip_safe=False,
    include_package_data=True,
    platforms="any",
    install_requires=requirements,
    setup_requires=requirements,
    extras_require=optional_requirements,
    keywords=[
        "flask",
        "extension",
        "minifer",
        "htmlmin",
        "lesscpy",
        "jsmin",
        "html",
        "js",
        "less",
        "css",
    ],
    classifiers=[
        *supported_python_classifiers,
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
