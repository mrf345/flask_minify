<h1 align='center'> flask_minify </h1>
<p align='center'>
<a href='https://pypi.org/project/Flask-Minify/'>
    <img src='https://img.shields.io/github/v/tag/mrf345/flask_minify' alt='Latest Release' />
</a>
<a href='https://github.com/mrf345/flask_minify/actions/workflows/ci.yml'>
  <img src='https://github.com/mrf345/flask_minify/workflows/Build/badge.svg'>
</a>
<a href='https://github.com/mrf345/flask_minify/actions/workflows/ci.yml'>
  <img src='https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/mrf345/bc746d7bfe356b54fbb93b2ea5d0d2a4/raw/flask_minify__heads_master.json' alt='Coverage Percentage' />
</a>
<br />
<a href='https://github.com/psf/black'>
    <img src='https://img.shields.io/badge/code%20style-black-000000.svg' alt='Code Style Black' />
</a>
<img src='https://img.shields.io/pypi/pyversions/flask_minify' alt='Supported versions' />
<br />
</p>

<h3 align='center'>Flask extension to parse and minify html, javascript, css and less.</h3>

## Install:

With **pip**

- `pip install Flask-Minify`

*Or* from the source

- `git clone https://github.com/mrf345/flask_minify.git`
- `cd flask_minify`
- `python setup.py install`

## Setup:

In this example the  extension will minify every HTML request, unless it's explicitly bypassed.

```python
from flask import Flask
from flask_minify import minify

app = Flask(__name__)
minify(app=app, html=True, js=True, cssless=True)
```

Another approach is using **decorators**, you can set the extension to be `passive` so will only minify the decorated routes

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


Option             | type     | Description
-------------------|----------|-------------
 app               | `object` | `Flask` app instance to be passed (default: `None`)
 html              | `bool`   | minify HTML (default: `True`)
 js                | `bool`   | minify JavaScript output (default: `True`)
 cssless           | `bool`   | minify CSS or Less. (default: `True`)
 fail_safe         | `bool`   | avoid raising error while minifying (default: `True`)
 bypass            | `list`   | endpoints to bypass minifying for, supports `Regex` (default: `[]`)
 bypass_caching    | `list`   | endpoints to bypass caching for, supports `Regex` (default: `[]`)
 caching_limit     | `int`    | limit the number of cached response variations (default: `2`).
 passive           | `bool`   | disable active minifying, to use *decorators* instead (default: `False`)
 static            | `bool`   | enable minifying static files css, less and js (default: `True`)
 script_types      | `list`   | script types to limit js minification to (default: `[]`)
 parsers           | `dict`   | parsers to handle minifying specific tags, mainly for advanced customization (default: `{}`)
 parser_precedence | `bool`   | allow parser specific options to take precedence over the extension (default: `False`)


#### - `bypass` and `bypass_caching`

`endpoint` in this context is the name of the function decorated with `@app.route`
so in the following example the endpoint will be `root`:

```python
@app.route('/root/<id>')
def root(id):
    return id
```

both options can handle regex patterns as input so for example, if you want to bypass all routes on a certain blueprint
you can just pass the pattern as such:

```python
minify(app, bypass=['blueprint_name.*'])
```

#### - `caching_limit`

if the option is set to `0`, we'll not cache any response, so if you want to **disable caching** just do that.


#### - `script_types`

when using the option include `''` (empty string) in the list to include script blocks which are missing the `type` attribute.

#### - `parsers`

using `parser` allows to pass tag specific options to the module responsible for the minification, as well as replacing the default
parser with another included option or your own custom one. In the following example will replace the default `style` (handles CSS)
parser `rcssmin` with `lesscpy`:

```python
from flask_minify import minify
from flask_minify.parsers import as minify_parsers

parsers = {'style': minify_parsers.Lesscpy}

minify(app=app, parsers=parsers)
```

you can override the default parser runtime options as well, as shown in the following example:

```python
from flask_minify import minify
from flask_minify.parsers import as minify_parsers

class CustomCssParser(minify_parsers.Lesscpy):
    runtime_options = {
        **minify_parsers.Lesscpy.runtime_options,
        "xminify": False,
    }

parsers = {'style': CustomCssParser}

minify(app=app, parsers=parsers)
```

the **default** parsers are set to `{"html": Html, "script": Jsmin, "style": Lesscpy}` check [the code](https://github.com/mrf345/flask_minify/blob/master/flask_minify/parsers.py) out for more insight.


## Development:

- *Tests*: `make test`
- *Style check*: `make lint`
- *Format code*: `make format`

## Breaking changes

#### `0.33`

introduces a breaking change to the expected output, in this release `lesscpy` will be replaced by `cssmin` as
the default css minifier so no more `less` compiling by default. in case you don't want that, follow [this example](https://github.com/mrf345/flask_minify#--parsers). 