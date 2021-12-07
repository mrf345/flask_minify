import os

from flask import send_from_directory
from pytest import fixture
from xxhash import xxh64

from .constants import (
    FALSE_LESS,
    HTML,
    JS,
    JS_RAW,
    JS_WITH_TYPE,
    LESS,
    LESS_RAW,
    MINIFED_HTML,
    MINIFED_HTML_EMBEDDED_TAGS,
    MINIFED_LESS,
    MINIFIED_JS,
    MINIFIED_JS_RAW,
    MINIFIED_JS_WITH_TYPE,
    MINIFIED_LESS_RAW,
)
from .setup import app, html_decorated, store_minify


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
    store_minify.parser.runtime_options["html"]["minify_inline"] = {
        "script": True,
        "style": True,
    }
    store_minify.parser.runtime_options["html"]["script_types"] = []
    app.config["TESTING"] = True

    files = {
        "./test.js": JS_RAW,
        "./test.less": LESS_RAW,
        "./test.bypass.css": LESS_RAW,
    }
    files_items = getattr(files, "iteritems", getattr(files, "items", None))()

    for f, c in files_items:
        with open(f, "w+") as file:
            file.write(c)

    with app.test_client() as client:
        yield client

    for f, c in files_items:
        try:
            os.remove(f)
        except Exception as e:
            pass


def test_html_minify(client):
    """testing HTML minify option"""
    resp = client.get("/html")
    assert MINIFED_HTML == resp.data


def test_html_bypassing(client):
    """testing HTML route bypassing"""
    store_minify.bypass.append("html")
    resp = client.get("/html")
    assert bytes(HTML.encode("utf-8")) == resp.data


def test_javascript_minify(client):
    """testing JavaScript minify option"""
    resp = client.get("/js")
    assert MINIFIED_JS == resp.data


def test_lesscss_minify(client):
    """testing css and less minify option"""
    store_minify.cssless = True
    resp = client.get("/cssless")
    assert MINIFED_LESS == resp.data


def test_minify_cache(client):
    """testing caching minifed response"""
    store_minify.caching_limit = 10
    client.get("/cssless")  # hit it twice, to get the cached minified response
    resp = client.get("/cssless").data

    assert resp == MINIFED_LESS
    assert (
        MINIFED_LESS.decode("utf-8") in store_minify.cache.get("cssless", {}).values()
    )


def test_fail_safe(client):
    """testing fail safe enabled with false input"""
    store_minify.parser.fail_safe = True
    resp = client.get("/cssless_false")

    assert bytes(FALSE_LESS.encode("utf-8")) == resp.data


def test_fail_safe_false_input(client):
    """testing fail safe disabled with false input"""
    try:
        client.get("/cssless_false")
    except Exception as e:
        assert "CompilationError" == e.__class__.__name__


def test_caching_limit_only_when_needed(client):
    """test caching limit without any variations"""
    store_minify.caching_limit = 5
    store_minify.cssless = True
    resp = [client.get("/cssless").data for i in range(10)]

    assert len(store_minify.cache.get("cssless", {})) == 1
    for r in resp:
        assert MINIFED_LESS == r


def test_caching_limit_exceeding(client):
    """test caching limit with multiple variations"""
    store_minify.caching_limit = 4
    resp = [client.get("/js/{}".format(i)).data for i in range(10)]

    assert len(store_minify.cache.get("js_addition", {})) == store_minify.caching_limit

    for v in store_minify.cache.get("js_addition", {}).values():
        assert bytes(v.encode("utf-8")) in resp


def test_bypass_caching(client):
    """test endpoint bypassed not caching"""
    store_minify.bypass_caching.append("cssless")
    resp = client.get("/cssless")
    resp_values = [
        bytes("<style>{}</style>".format(v).encode("utf-8"))
        for v in store_minify.cache.get("cssless", {}).values()
    ]

    assert MINIFED_LESS == resp.data
    assert resp.data not in resp_values


def test_bypassing_with_regex(client):
    """test endpoint bypassed not minifying and not caching regex"""
    store_minify.bypass.append("css*")
    store_minify.bypass_caching.append("css*")
    store_minify.fail_safe = True
    resp = client.get("/cssless").data.decode("utf-8")
    resp_false = client.get("/cssless_false").data.decode("utf-8")

    assert resp == LESS
    assert resp_false == FALSE_LESS


def test_passive_flag(client):
    """test disabling active minifying"""
    store_minify.passive = True
    resp = client.get("/html").data.decode("utf-8")

    assert resp == HTML


def test_html_minify_decorated(client):
    """test minifying html decorator"""
    store_minify.passive = True
    resp = client.get("/html_decorated").data

    assert resp == MINIFED_HTML


def test_html_minify_decorated_cache(client):
    store_minify.passive = True
    client.get("/html_decorated").data
    resp = client.get("/html_decorated").data
    hash_key = xxh64(HTML).hexdigest()
    cache_tuple = html_decorated.__wrapped__.minify

    assert resp == MINIFED_HTML
    assert cache_tuple == (hash_key, resp.decode("utf-8"))


def test_javascript_minify_decorated(client):
    """test minifying javascript decorator"""
    store_minify.passive = True
    resp = client.get("/js_decorated").data

    assert resp == MINIFIED_JS


def test_minify_less_decorated(client):
    """test minifying css/less decorator"""
    store_minify.passive = True
    resp = client.get("/less_decorated").data

    assert resp == MINIFED_LESS


def test_minify_static_js_with_add_url_rule(client):
    """test minifying static file js"""
    f = "/test.js"

    with app.app_context():
        app.add_url_rule(
            f,
            f,
            lambda: send_from_directory(
                "../.", f[1:], mimetype="application/javascript"
            ),
        )

    store_minify.static = True
    assert client.get(f).data == MINIFIED_JS_RAW

    store_minify.static = False
    assert client.get(f).data != MINIFIED_JS_RAW

    store_minify.static = True
    store_minify.js = False
    assert client.get(f).data != MINIFIED_JS_RAW


def test_minify_static_less_with_add_url_rule(client):
    """test minifying static file less"""
    f = "/test.less"

    with app.app_context():
        app.add_url_rule(
            f,
            f,
            lambda: send_from_directory("../.", f[1:], mimetype="application/less"),
        )

    store_minify.static = True
    assert client.get(f).data == MINIFIED_LESS_RAW

    store_minify.static = False
    assert client.get(f).data != MINIFIED_LESS_RAW

    store_minify.static = True
    store_minify.cssless = False
    assert client.get(f).data != MINIFIED_LESS_RAW


def test_bypass_minify_static_file(client):
    """test bypassing css file minifying"""
    f = "/test.bypass.css"

    with app.app_context():
        app.add_url_rule(
            f, f, lambda: send_from_directory("../.", f[1:], mimetype="application/css")
        )

    store_minify.static = True
    assert client.get(f).data == MINIFIED_LESS_RAW

    store_minify.bypass = ["bypass.*"]
    assert client.get(f).data != MINIFIED_LESS_RAW


def test_script_types(client):
    """test script types with empty type."""
    store_minify.parser.runtime_options["html"]["script_types"] = [
        "application/javascript"
    ]
    assert client.get("/js").data == bytes(JS.encode("utf-8"))

    store_minify.parser.runtime_options["html"]["script_types"] = [
        "application/javascript"
    ]
    assert client.get("/js_with_type").data == MINIFIED_JS_WITH_TYPE

    store_minify.cache = {}
    store_minify.parser.runtime_options["html"]["script_types"] = [
        "testing",
        "text/javascript",
    ]
    assert client.get("/js_with_type").data == bytes(JS_WITH_TYPE.encode("utf-8"))


def test_html_with_embedded_tags(client):
    """test html with embedded js and less tags"""
    assert client.get("/html_embedded").data == MINIFED_HTML_EMBEDDED_TAGS


def test_unicode_endpoint(client):
    """test endpoint with ascii chars"""
    resp = client.get("/unicode")

    assert resp.status == "200 OK"
    assert resp.data.decode("utf-8") == "–"


if __name__ == "__main__":
    app.run()
