from pytest import fixture
from flask import Flask
from flask_minify import minify

app = Flask(__name__)
store_minify = minify(app=app)


@app.route('/html')
def html():
    return '''<html>
            <body>
                <h1>
                    HTML
                </h1>
            </body>
        </html>'''


@app.route('/bypassed')
def bypassed():
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
    return '''<style>
        body {
            color: red;;
        }
    </style>'''


@fixture
def client():
    app.config['TESTING'] = True
    client = app.test_client()
    yield client


def test_html_minify(client):
    """ testing HTML minify option """
    resp = client.get('/html')
    assert b'<html> <body> <h1> HTML </h1> </body> </html>' == resp.data


def test_html_bypassing(client):
    """ testing HTML route bypassing """
    store_minify.bypass.append('/html')
    resp = client.get('/html')
    assert b'<html> <body> <h1> HTML </h1> </body> </html>' != resp.data


def test_javascript_minify(client):
    """ testing JavaScript minify option """
    resp = client.get('/js')
    assert b'<script>["J","S"].reduce(function(a,r){return a+r})</script>' == resp.data


def test_lesscss_minify(client):
    """ testing css and less minify option """
    store_minify.cssless = True
    resp = client.get('/cssless')
    assert b'<style>body{color:red;}</style>' == resp.data


def test_minify_cache(client):
    """ testing caching minifed response """
    store_minify.caching_limit = 10
    client.get('/cssless')  # hit it twice, to get the cached minified response
    resp = client.get('/cssless').data

    assert resp.decode('utf8').replace('<style>', '')\
                              .replace('</style>', '') in\
        store_minify.cache.get('/cssless', {}).values()


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


def test_fail_safe(client):
    """ testing fail safe enabled with false input """
    store_minify.cssless = False
    resp = client.get('/cssless_false')
    assert b'''<style>
        body {
            color: red;;
        }
    </style>''' == resp.data


def test_fail_safe_false_input(client):
    """testing fail safe disabled with false input """
    store_minify.fail_safe = False
    try:
        client.get('/cssless_false')
    except Exception as e:
        raise e
        assert 'CompilationError' == e.__class__.__name__


def test_caching_limit_only_when_needed(client):
    """test caching limit without any variations """
    store_minify.caching_limit = 5
    store_minify.cssless = True
    resp = [client.get('/cssless').data for i in range(10)]

    assert len(store_minify.cache.get('/cssless', {})) == 1
    for r in resp:
        assert b'<style>body{color:red;}</style>' == r


def test_caching_limit_exceeding(client):
    """test caching limit with multiple variations """
    resp = [client.get('/js/{}'.format(i)).data for i in range(10)]

    assert len(store_minify.cache.get('/js/<addition>', {}))\
        == store_minify.caching_limit
    for i, r in enumerate(resp[:store_minify.caching_limit]):
        assert bytes((
            '<script>["J","S"].reduce(function(a,r){return a+r});' +
            str(i) + '</script>').encode('utf-8')) == r
        assert r in [
            bytes(('<script>' + c + '</script>').encode('utf-8')) for c in
            store_minify.cache.get('/js/<addition>', {}).values()]


if __name__ == '__main__':
    app.run()
