from flask import Flask

from flask_minify import minify
from flask_minify import parsers as minify_parsers
from flask_minify.decorators import minify as decorator

from .constants import (
    CSS_EDGE_CASES,
    FALSE_JS,
    FALSE_LESS,
    HTML,
    HTML_CONDITIONAL_COMMENTS,
    HTML_EMBEDDED_TAGS,
    JS,
    JS_WITH_TYPE,
    LESS,
)


def create_app(go=True):
    app = Flask(__name__)
    parsers = {"style": minify_parsers.Lesscpy}
    store_minify = minify(
        app=app,
        fail_safe=False,
        go=go,
        parsers={} if go else parsers,
    )

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

    @app.route("/js_false")
    def js_false():
        return FALSE_JS

    @app.route("/html_decorated")
    @decorator(html=True, go=go)
    def html_decorated():
        return HTML

    @app.route("/js_decorated")
    @decorator(html=True, js=True, go=go)
    def js_decorated():
        return JS

    @app.route("/less_decorated")
    @decorator(html=True, cssless=True, parsers=parsers, go=go)
    def less_decorated():
        return LESS

    @app.route("/css_decorated")
    @decorator(html=True, cssless=True, go=go)
    def css_decorated():
        return f"<style>{CSS_EDGE_CASES}</style>"

    @app.route("/html_embedded")
    @decorator(html=True, js=True, cssless=True, go=go)
    def html_embedded():
        return HTML_EMBEDDED_TAGS

    @app.route("/unicode")
    def unicode_endpoint():
        return "–"

    @app.route("/conditional-comments")
    def conditional_comments():
        return HTML_CONDITIONAL_COMMENTS

    return app, store_minify
