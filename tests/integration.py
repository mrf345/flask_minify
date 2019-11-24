from sys import path as sys_path
from os import path
from importlib import import_module
from pytest import fixture
from flask import Flask

from constants import (
    HTML, JS, LESS, MINIFED_HTML, MINIFIED_JS,
    MINIFED_LESS, FALSE_LESS, MINIFED_STRIPED)


sys_path.append(path.dirname(path.dirname(__file__)))
minify = import_module('flask_minify').minify


app = Flask(__name__)
store_minify = minify(app=app, fail_safe=False)


@app.route('/html')
def html():
    return HTML


@app.route('/bypassed')
def bypassed():
    return HTML


@app.route('/js')
def js():
    return JS


@app.route('/cssless')
def cssless():
    return LESS


@app.route('/js/<addition>')
def js_addition(addition=None):
    return '''<script>
        ["J", "S"].reduce(
            function (a, r) {
                return a + r
            })
    ''' + (addition + '\n</script>')


@app.route('/cssless_false')
def cssless_false():
    return FALSE_LESS


@fixture
def client():
    store_minify.fail_safe = False
    store_minify.cssless = True
    store_minify.js = True
    store_minify.caching_limit = 1
    store_minify.bypass_caching = []
    store_minify.cache = {}
    app.config['TESTING'] = True
    client = app.test_client()
    yield client


def test_html_minify(client):
    """ testing HTML minify option """
    resp = client.get('/html')
    assert MINIFED_HTML == resp.data


def test_html_bypassing(client):
    """ testing HTML route bypassing """
    store_minify.bypass.append('html')
    resp = client.get('/html')
    assert bytes(HTML.encode('utf-8')) == resp.data


def test_javascript_minify(client):
    """ testing JavaScript minify option """
    resp = client.get('/js')
    assert MINIFIED_JS == resp.data


def test_lesscss_minify(client):
    """ testing css and less minify option """
    store_minify.cssless = True
    resp = client.get('/cssless')
    assert MINIFED_LESS == resp.data


def test_minify_cache(client):
    """ testing caching minifed response """
    store_minify.caching_limit = 10
    client.get('/cssless')  # hit it twice, to get the cached minified response
    resp = client.get('/cssless').data

    assert resp == MINIFED_LESS
    assert MINIFED_STRIPED('MINIFED_LESS').decode('utf-8') in\
        store_minify.cache.get('cssless', {}).values()


def test_fail_safe(client):
    """ testing fail safe enabled with false input """
    store_minify.fail_safe = True
    store_minify.cssless = False
    resp = client.get('/cssless_false')

    assert bytes(FALSE_LESS.encode('utf-8')) == resp.data


def test_fail_safe_false_input(client):
    """testing fail safe disabled with false input """
    try:
        client.get('/cssless_false')
    except Exception as e:
        assert 'CompilationError' == e.__class__.__name__


def test_caching_limit_only_when_needed(client):
    """test caching limit without any variations """
    store_minify.caching_limit = 5
    store_minify.cssless = True
    resp = [client.get('/cssless').data for i in range(10)]

    assert len(store_minify.cache.get('cssless', {})) == 1
    for r in resp:
        assert MINIFED_LESS == r


def test_caching_limit_exceeding(client):
    """test caching limit with multiple variations """
    resp = [client.get('/js/{}'.format(i)).data for i in range(10)]

    assert len(store_minify.cache.get('js_addition', {}))\
        == store_minify.caching_limit
    for i, r in enumerate(resp[:store_minify.caching_limit]):
        assert bytes((
            '<script>["J","S"].reduce(function(a,r){return a+r});' +
            str(i) + '</script>').encode('utf-8')) == r
        assert r in [
            bytes(('<script>' + c + '</script>').encode('utf-8')) for c in
            store_minify.cache.get('js_addition', {}).values()]


def test_bypass_caching(client):
    """test endpoint bypassed not caching"""
    store_minify.bypass_caching.append('cssless')
    resp = client.get('/cssless')
    resp_values = [
        bytes('<style>{}</style>'.format(v).encode('utf-8')) for v in
        store_minify.cache.get('cssless', {}).values()]

    assert MINIFED_LESS == resp.data
    assert resp.data not in resp_values


def test_bypassing_with_regex(client):
    """test endpoint bypassed not minifying and not caching regex"""
    store_minify.bypass.append('css*')
    store_minify.bypass_caching.append('css*')
    store_minify.fail_safe = True
    resp = client.get('/cssless').data.decode('utf-8')
    resp_false = client.get('/cssless_false').data.decode('utf-8')

    assert resp == LESS
    assert resp_false == FALSE_LESS


if __name__ == '__main__':
    app.run()
