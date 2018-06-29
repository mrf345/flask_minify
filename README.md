<h1 align='center'> flask_minify </h1>
<p align='center'>
<a href='https://travis-ci.com/mrf345/flask_minify'><img src='https://travis-ci.com/mrf345/flask_minify.svg?branch=master'></a><a href='https://coveralls.io/github/mrf345/flask_minify?branch=master'><img src='https://coveralls.io/repos/github/mrf345/flask_minify/badge.svg?branch=master' alt='Coverage Status' /></a>
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
def __init__(self,
  app=None,
  html=True,
  js=False,
  cssless=True,
  cache=True):
  """
    A Flask extension to minify flask response for html,
    javascript, css and less.
    @param: app Flask app instance to be passed (default:None).
    @param: js To minify the css output (default:False).
    @param: cssless To minify spaces in css (default:True).
    @param: cache To cache minifed response with hash (default: True).
  """
```

## Credit:
> - [htmlmin][1322354e]: HTML python minifier.
> - [lesscpy][1322353e]: Python less compiler and css minifier.
> - [jsmin][1322355e]: JavaScript python minifier.

[1322353e]: https://github.com/lesscpy/lesscpy "lesscpy repo"
[1322354e]: https://github.com/mankyd/htmlmin "htmlmin repo"
[1322355e]: https://github.com/tikitu/jsmin "jsmin repo"