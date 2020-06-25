<h1 align='center'> flask_minify </h1>
<p align='center'>
<a href='https://travis-ci.com/mrf345/flask_minify'>
  <img src='https://travis-ci.com/mrf345/flask_minify.svg?branch=master'>
</a>
<img src='https://img.shields.io/github/v/tag/mrf345/flask_minify' alt='Latest Release' />
<br />
<img src='https://img.shields.io/pypi/pyversions/flask_minify' alt='Supported versions' />
<br />
<a href='https://coveralls.io/github/mrf345/flask_minify?branch=master'>
  <img src='https://coveralls.io/repos/github/mrf345/flask_minify/badge.svg?branch=master' alt='Coverage Status' />
</a>
<img src='https://img.shields.io/badge/code%20style-pep8-orange.svg' alt='Code Style' />
<img src='https://img.shields.io/pypi/dm/flask_minify' alt='Number of downloads' />
</p>
<h3 align='center'>A Flask extension to parse request's response and minify html, javascript, css and less.</h3>

## Install:
#### - With pip
> - `pip install Flask-Minify` <br />

#### - From the source:
> - `git clone https://github.com/mrf345/flask_minify.git`<br />
> - `cd flask_minify` <br />
> - `python setup.py install`

## Setup:
> With this setup the extension will minify every HTML request, unless it's explicitly bypassed.
```python
from flask import Flask
from flask_minify import minify

app = Flask(__name__)
minify(app=app, html=True, js=True, cssless=True)
```

#### - Using a decorator instead:
> You can set the extension to be passive so it will minify only the decorated routes.

```python
from flask import Flask
from flask_minify import minify, decorators

app = Flask(__name__)
minify(app=app, passive=True)

@app.route('/')
@decorators.minify(html=True, js=True, cssless=True)
def example():
  return '<h1>Example...</h1>'
```

## Options:
```python
def __init__(
        self, app=None, html=True, js=True, cssless=True,
        fail_safe=True, bypass=[], bypass_caching=[], caching_limit=2,
        passive=False, static=True
    ):
        ''' Extension to minify flask response for html, javascript, css and less.

        Parameters
        ----------
            app: Flask.app
                Flask app instance to be passed.
            js: bool
                To minify the js output.
            cssless: bool
                To minify spaces in css.
            fail_safe: bool
                to avoid raising error while minifying.
            bypass: list
                list of endpoints to bypass minifying for. (Regex)
            bypass_caching: list
                list of endpoints to bypass caching for. (Regex)
            caching_limit: int
                to limit the number of minified response variations.
            passive: bool
                to disable active minifying.
            static: bool
                to enable minifying static files css, less and js.

        Notes
        -----
        if `caching_limit` is set to 0, we'll not cache any endpoint responses,
        so if you want to disable caching just do that.

        `endpoint` is the name of the function decorated with the
        `@app.route()` so in the following example the endpoint will be `root`:
            @app.route('/root/<id>')
            def root(id):
                return id

        when using a `Blueprint` the decorated endpoint will be suffixed with
        the blueprint name; `Blueprint('blueprint_name')` so here the endpoint
        will be `blueprint_name.root`.

        `bypass` and `bypass_caching` can handle regex patterns so if you want
        to bypass all routes on a certain blueprint you can just pass
        the pattern as such:
            minify(app, bypass=['blueprint_name.*'])
        '''
```

## Development:
- **Run Tests:** `pytest`
- **Run style checks:** `flake8`
