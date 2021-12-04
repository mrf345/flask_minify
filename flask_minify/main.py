from itertools import tee
from re import compile as compile_re
from sys import maxsize

from flask import _app_ctx_stack, request
from xxhash import xxh32, xxh64

from flask_minify.parsers import Html, Jsmin, Lesscpy, Parser
from flask_minify.utils import is_cssless, is_html, is_js

# optimized hashing speed based on cpu architecture
hashing = xxh64 if maxsize > 2 ** 32 else xxh32


class Minify:
    "Extension to minify flask response for html, javascript, css and less."

    def __init__(
        self,
        app=None,
        html=True,
        js=True,
        cssless=True,
        fail_safe=True,
        bypass=[],
        bypass_caching=[],
        caching_limit=2,
        passive=False,
        static=True,
        script_types=[],
        parsers={},
        parser_precedence=False,
    ):
        """Extension to minify flask response for html, javascript, css and less.

        Parameters
        ----------
        app: Flask.app
            Flask app instance to be passed.
        html: bool
            to minify HTML.
        js: bool
            to minify JavaScript output.
        cssless: bool
            to minify CSS or Less.
        fail_safe: bool
            to avoid raising error while minifying.
        bypass: list
            list of endpoints to bypass minifying for. (Regex)
        bypass_caching: list
            list of endpoints to bypass caching for. (Regex)
        caching_limit: int
            to limit the number of minified response variations.
        passive: bool
            to disable active minifying.
        static: bool
            to enable minifying static files css, less and js.
        script_types: list
            list of script types to limit js minification to.
        parsers: dict
            parsers to handle minifying specific tags.
        parser_precedence: bool
            allow parser specific options to take precedence over the extension.

        Notes
        -----
        if `caching_limit` is set to 0, we'll not cache any endpoint responses,
        so if you want to disable caching just do that.

        `endpoint` is the name of the function decorated with the
        `@app.route()` so in the following example the endpoint will be `root`:
            @app.route('/root/<id>')
            def root(id):
                return id

        when using a `Blueprint` the decorated endpoint will be suffixed with
        the blueprint name; `Blueprint('blueprint_name')` so here the endpoint
        will be `blueprint_name.root`.

        `bypass` and `bypass_caching` can handle regex patterns so if you want
        to bypass all routes on a certain blueprint you can just pass
        the pattern as such:
            minify(app, bypass=['blueprint_name.*'])

        when using `script_types` include '' (empty string) in the list to
        include script blocks which are missing the type attribute.
        """
        self.html = html
        self.js = js
        self.script_types = script_types
        self.cssless = cssless
        self.fail_safe = fail_safe
        self.bypass = bypass
        self.bypass_caching = bypass_caching
        self.caching_limit = caching_limit
        self.cache = {}
        self._app = app
        self.passive = passive
        self.static = static
        runtime_options = {
            "html": {
                "only_html_content": not html,
                "script_types": script_types,
                "minify_inline": {
                    "script": js,
                    "style": cssless,
                },
            },
        }
        self.parser = Parser(parsers, runtime_options, fail_safe, parser_precedence)

        app and self.init_app(app)

    @staticmethod
    def get_endpoint_matches(endpoint, patterns):
        """Get the patterns that matches the current endpoint.

        Parameters
        ----------
        endpoint: str
            to finds the matches for.
        patterns: list
            regex patterns or strings to match endpoint.

        Returns
        -------
        list
            patterns that match the current endpoint.
        """
        matches, x = tee(
            compiled_pattern
            for compiled_pattern in (compile_re(p) for p in patterns)
            if compiled_pattern.search(endpoint)
        )
        has_matches = bool(next(x, 0))

        return matches, has_matches

    @property
    def app(self):
        """If app was passed take it, if not get the one on top.

        Returns
        -------
        Flask App
            The current Flask application.
        """
        return self._app or (_app_ctx_stack.top and _app_ctx_stack.top.app)

    @property
    def endpoint(self):
        """Get the current response endpoint, with a failsafe.

        Returns
        -------
        str
            the current endpoint.
        """
        with self.app.app_context():
            path = getattr(request, "endpoint", "") or ""

            if path == "static":
                path = getattr(request, "path", "") or ""

            return path

    def init_app(self, app):
        """Handle initiation of multiple apps NOTE:Factory Method"""
        app.after_request(self.main)
        app.teardown_appcontext(self.teardown)

    def teardown(self, exception):
        """Nothing todo on app context teardown XXX:Factory Method"""
        pass

    def get_minified_or_cached(self, content, tag):
        """Check if the content is already cached and restore or store it.

        Parameters
        ----------
        content: str
            a script or style html tag content.
        tag: bool
            html tag the content belongs to.

        Returns
        -------
        str
            stored or restored minifed content.
        """

        def _cache_dict():
            return self.cache.get(self.endpoint, {})

        key = hashing(content.encode("utf-8")).hexdigest()
        limit_reached = len(_cache_dict()) >= self.caching_limit
        _, bypassed = self.get_endpoint_matches(self.endpoint, self.bypass_caching)

        def _cached():
            return _cache_dict().get(key)

        def _minified():
            return self.parser.minify(content, tag)

        if not _cached() and not bypassed:
            if limit_reached and _cache_dict():
                _cache_dict().popitem()

            self.cache.setdefault(self.endpoint, {}).update({key: _minified()})

        return _cached() or _minified()

    def main(self, response):
        """Where a dragon once lived!

        Parameters
        ----------
        response: Flask.response
            instance form the `after_request` handler.

        Returns
        -------
        Flask.Response
            minified flask response if it fits the requirements.
        """
        html = is_html(response)
        cssless = is_cssless(response)
        js = is_js(response)
        _, bypassed = self.get_endpoint_matches(self.endpoint, self.bypass)
        should_bypass = bypassed or self.passive
        should_minify = any(
            [
                html and self.html,
                cssless and self.cssless,
                js and self.js,
            ]
        )

        if should_minify and not should_bypass:
            response.direct_passthrough = False
            text = response.get_data(as_text=True)
            tag = "html" if html else "script" if js else "style"

            if html or (self.static and any([cssless, js])):
                response.set_data(self.get_minified_or_cached(text, tag))

        return response
