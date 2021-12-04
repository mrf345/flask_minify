from flask import Flask

from flask_minify import minify
from flask_minify import parsers as minify_parsers
from flask_minify.decorators import minify as decorator

from .constants import FALSE_LESS, HTML, HTML_EMBEDDED_TAGS, JS, JS_WITH_TYPE, LESS

app = Flask(__name__)
parsers = {"style": minify_parsers.Lesscpy}
store_minify = minify(app=app, fail_safe=False, parsers=parsers)


@app.route("/html")
def html():
    return HTML


@app.route("/bypassed")
def bypassed():
    return HTML


@app.route("/js")
def js():
    return JS


@app.route("/js_with_type")
def js_with_type():
    return JS_WITH_TYPE


@app.route("/cssless")
def cssless():
    return LESS


@app.route("/js/<addition>")
def js_addition(addition=None):
    return """<script>
        ["J", "S"].reduce(
            function (a, r) {
                return a + r
            })
    """ + (
        addition + "\n</script>"
    )


@app.route("/cssless_false")
def cssless_false():
    return FALSE_LESS


@app.route("/html_decorated")
@decorator(html=True)
def html_decorated():
    return HTML


@app.route("/js_decorated")
@decorator(html=True, js=True)
def js_decorated():
    return JS


@app.route("/less_decorated")
@decorator(html=True, cssless=True, parsers=parsers)
def less_decorated():
    return LESS


@app.route("/html_embedded")
def html_embedded():
    return HTML_EMBEDDED_TAGS


@app.route("/unicode")
def unicode_endpoint():
    return u"–"
