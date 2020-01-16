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
<h3 align='center'>A Flask extension to minify flask response for html, javascript, css and less compilation as well.</h3>

## Install:
#### - With pip
> - `pip install Flask-Minify` <br />

#### - From the source:
> - `git clone https://github.com/mrf345/flask_minify.git`<br />
> - `cd flask_minify` <br />
> - `python setup.py install`

## Setup:
#### - Inside Flask app:

```python
from flask import Flask
from flask_minify import minify

app = Flask(__name__)
minify(app=app)
```

#### - Result:

> Before:
```html
<html>
  <head>
    <script>
      if (true) {
      	console.log('working !')
      }
    </script>
    <style>
      body {
      	background-color: red;
      }
    </style>
  </head>
  <body>
    <h1>Flask-Less Example !</h1>
  </body>
</html>
```
> After:
```html
<html> <head><script>if(true){console.log('working !')}</script><style>body{background-color:red;}</style></head> <body> <h1>Flask-Less Example !</h1> </body> </html>
```

## Options:
```python
def __init__(
        self, app=None, html=True, js=True, cssless=True,
        fail_safe=True, bypass=[], bypass_caching=[], caching_limit=1
    ):
        ''' Extension to minify flask response for html, javascript, css and less.

        Parameters
        ----------
            app: Flask.app
                Flask app instance to be passed.
            js: bool
                To minify the css output.
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

            NOTE: if `caching_limit` is set to 0, we'll not cache any endpoint
                  response, so if you want to disable caching just do that.

            EXAMPLE: endpoint is the name of the function decorated with the
                    `@app.route()` so in the following example the endpoint
                    will be `root`:

                     @app.route('/root/<id>')
                     def root(id):
                         return id

            NOTE: when using a `Blueprint` the decorated endpoint will be
                  suffixed with the blueprint name;
                  `Blueprint('blueprint_name')` so here the endpoint will be
                  `blueprint_name.root`.

                  `bypass` and `bypass_caching` can handle regex patterns so if
                  you want to bypass all routes on a certain blueprint you can
                  just pass the pattern as such:
                  minify(app, bypass=['blueprint_name.*'])
        '''
```

## Credit:
> - [htmlmin][1322354e]: HTML python minifier.
> - [lesscpy][1322353e]: Python less compiler and css minifier.
> - [jsmin][1322355e]: JavaScript python minifier.

[1322353e]: https://github.com/lesscpy/lesscpy "lesscpy repo"
[1322354e]: https://github.com/mankyd/htmlmin "htmlmin repo"
[1322355e]: https://github.com/tikitu/jsmin "jsmin repo"