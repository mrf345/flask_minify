from os import close, unlink
from tempfile import mkstemp
from pytest import fixture
from hashlib import md5
from flask import Flask
from flask_minify import minify

app = Flask(__name__)


@app.route('/html')
def html():
    return '''<html>
            <body>
                <h1>
                    HTML
                </h1>
            </body>
        </html>'''

@app.route('/js')
def js():
    return '''<script>
        ["J", "S"].reduce(
            function (a, r) {
                return a + r 
            })
    </script>'''

@app.route('/cssless')
def cssless():
    return '''<style>
        @a: red;
        body {
            color: @a;
        }
    </style>'''

@fixture
def client():
    app.config['TESTING'] = True
    client = app.test_client()
    yield client


def test_html_minify(client):
    """ testing HTML minify option """
    minify(app=app, html=True, cssless=False, js=False)
    resp = client.get('/html')
    assert b'<html> <body> <h1> HTML </h1> </body> </html>' == resp.data

def test_javascript_minify(client):
    """ testing JavaScript minify option """
    minify(app=app, html=False, cssless=False, js=True)
    resp = client.get('/js')
    assert b'<script>["J","S"].reduce(function(a,r){return a+r})</script>' == resp.data

def test_lesscss_minify(client):
    """ testing css and less minify option """
    minify(app=app, html=False, cssless=True, js=False)
    resp = client.get('/cssless')
    assert b'<style>body{color:red;}</style>' == resp.data

def test_minify_cache(client):
    """ testing caching minified response """
    minify_store = minify(app=app, js=False, cssless=False, cache=True)
    client.get('/html').data # to cover hashing return
    resp = client.get('/html').data
    assert resp in minify_store.history.values()

def test_false_input(client):
    """ testing false input for raise coverage """
    try:
        minify(app=None)
    except Exception as e:
        assert type(e) is AttributeError
    try:
        minify(app, 'nothing', 'nothing')
    except Exception as e:
        assert type(e) is TypeError
