import os
from pytest import fixture
from flask import send_from_directory

from .setup import store_minify, app
from .constants import (HTML, LESS, FALSE_LESS, MINIFED_HTML, MINIFIED_JS,
                        MINIFED_LESS, MINIFIED_JS_RAW, MINIFIED_LESS_RAW, JS,
                        JS_RAW, LESS_RAW, JS_WITH_TYPE, MINIFIED_JS_WITH_TYPE,
                        MINIFED_HTML_EMBEDDED_TAGS)


@fixture
def client():
    store_minify.fail_safe = False
    store_minify.cssless = True
    store_minify.js = True
    store_minify.caching_limit = 0
    store_minify.bypass = []
    store_minify.bypass_caching = []
    store_minify.cache = {}
    store_minify.passive = False
    store_minify.script_types = []
    app.config['TESTING'] = True

    files = {'./test.js': JS_RAW,
             './test.less': LESS_RAW,
             './test.bypass.css': LESS_RAW}
    files_items = getattr(files, 'iteritems', getattr(files, 'items', None))()

    for f, c in files_items:
        with open(f, 'w+') as file:
            file.write(c)

    with app.test_client() as client:
        yield client

    for f, c in files_items:
        os.remove(f)


def test_html_minify(client):
    ''' testing HTML minify option '''
    resp = client.get('/html')
    assert MINIFED_HTML == resp.data


def test_html_bypassing(client):
    ''' testing HTML route bypassing '''
    store_minify.bypass.append('html')
    resp = client.get('/html')
    assert bytes(HTML.encode('utf-8')) == resp.data


def test_javascript_minify(client):
    ''' testing JavaScript minify option '''
    resp = client.get('/js')
    assert MINIFIED_JS == resp.data


def test_lesscss_minify(client):
    ''' testing css and less minify option '''
    store_minify.cssless = True
    resp = client.get('/cssless')
    assert MINIFED_LESS == resp.data


def test_minify_cache(client):
    ''' testing caching minifed response '''
    store_minify.caching_limit = 10
    client.get('/cssless')  # hit it twice, to get the cached minified response
    resp = client.get('/cssless').data

    assert resp == MINIFED_LESS
    assert MINIFED_LESS.decode('utf-8') in\
        store_minify.cache.get('cssless', {}).values()


def test_fail_safe(client):
    ''' testing fail safe enabled with false input '''
    store_minify.fail_safe = True
    store_minify.cssless = False
    resp = client.get('/cssless_false')

    assert bytes(FALSE_LESS.encode('utf-8')) == resp.data


def test_fail_safe_false_input(client):
    '''testing fail safe disabled with false input '''
    try:
        client.get('/cssless_false')
    except Exception as e:
        assert 'CompilationError' == e.__class__.__name__


def test_caching_limit_only_when_needed(client):
    '''test caching limit without any variations '''
    store_minify.caching_limit = 5
    store_minify.cssless = True
    resp = [client.get('/cssless').data for i in range(10)]

    assert len(store_minify.cache.get('cssless', {})) == 1
    for r in resp:
        assert MINIFED_LESS == r


def test_caching_limit_exceeding(client):
    '''test caching limit with multiple variations '''
    store_minify.caching_limit = 4
    resp = [client.get('/js/{}'.format(i)).data for i in range(10)]

    assert len(store_minify.cache.get('js_addition', {}))\
        == store_minify.caching_limit

    for v in store_minify.cache.get('js_addition', {}).values():
        assert bytes(v.encode('utf-8')) in resp


def test_bypass_caching(client):
    '''test endpoint bypassed not caching'''
    store_minify.bypass_caching.append('cssless')
    resp = client.get('/cssless')
    resp_values = [
        bytes('<style>{}</style>'.format(v).encode('utf-8')) for v in
        store_minify.cache.get('cssless', {}).values()]

    assert MINIFED_LESS == resp.data
    assert resp.data not in resp_values


def test_bypassing_with_regex(client):
    '''test endpoint bypassed not minifying and not caching regex'''
    store_minify.bypass.append('css*')
    store_minify.bypass_caching.append('css*')
    store_minify.fail_safe = True
    resp = client.get('/cssless').data.decode('utf-8')
    resp_false = client.get('/cssless_false').data.decode('utf-8')

    assert resp == LESS
    assert resp_false == FALSE_LESS


def test_passive_flag(client):
    '''test disabling active minifying'''
    store_minify.passive = True
    resp = client.get('/html').data.decode('utf-8')

    assert resp == HTML


def test_html_minify_decorated(client):
    '''test minifying html decorator'''
    store_minify.passive = True
    resp = client.get('/html_decorated').data

    assert resp == MINIFED_HTML


def test_javascript_minify_decorated(client):
    '''test minifying javascript decorator'''
    store_minify.passive = True
    resp = client.get('/js_decorated').data

    assert resp == MINIFIED_JS


def test_minify_less_decorated(client):
    '''test minifying css/less decorator'''
    store_minify.passive = True
    resp = client.get('/less_decorated').data

    assert resp == MINIFED_LESS


def test_minify_static_js_with_add_url_rule(client):
    '''test minifying static file js'''
    f = '/test.js'

    with app.app_context():
        app.add_url_rule(
            f, f,
            lambda: send_from_directory('../.',
                                        f[1:],
                                        mimetype='application/javascript'))

    store_minify.static = True
    assert client.get(f).data == MINIFIED_JS_RAW

    store_minify.static = False
    assert client.get(f).data.decode('utf-8') == JS_RAW

    store_minify.static = True
    store_minify.js = False
    assert client.get(f).data.decode('utf-8') == JS_RAW


def test_minify_static_less_with_add_url_rule(client):
    '''test minifying static file less'''
    f = '/test.less'

    with app.app_context():
        app.add_url_rule(
            f, f,
            lambda: send_from_directory('../.',
                                        f[1:],
                                        mimetype='application/less'))

    store_minify.static = True
    assert client.get(f).data == MINIFIED_LESS_RAW

    store_minify.static = False
    assert client.get(f).data.decode('utf-8') == LESS_RAW

    store_minify.static = True
    store_minify.cssless = False
    assert client.get(f).data.decode('utf-8') == LESS_RAW


def test_bypass_minify_static_file(client):
    '''test bypassing css file minifying'''
    f = '/test.bypass.css'

    with app.app_context():
        app.add_url_rule(
            f, f,
            lambda: send_from_directory('../.',
                                        f[1:],
                                        mimetype='application/css'))

    store_minify.static = True
    assert client.get(f).data == MINIFIED_LESS_RAW

    store_minify.bypass = ['bypass.*']
    assert client.get(f).data.decode('utf-8') == LESS_RAW


def test_script_types(client):
    '''test script types with empty type.'''
    store_minify.script_types = ['application/javascript']
    assert client.get('/js').data == bytes(JS.encode('utf-8'))

    store_minify.script_types = ['application/javascript']
    assert client.get('/js_with_type').data == MINIFIED_JS_WITH_TYPE

    store_minify.cache = {}
    store_minify.script_types = ['testing', 'text/javascript']
    assert client.get(
        '/js_with_type').data == bytes(JS_WITH_TYPE.encode('utf-8'))


def test_html_with_embedded_tags(client):
    '''test html with embedded js and less tags'''
    assert client.get('/html_embedded').data == MINIFED_HTML_EMBEDDED_TAGS


if __name__ == '__main__':
    app.run()
