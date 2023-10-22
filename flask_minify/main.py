from itertools import tee
from re import compile as compile_re

from flask import current_app, request

from flask_minify.cache import MemoryCache
from flask_minify.parsers import Parser
from flask_minify.utils import does_content_type_match


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
        go=True,
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
        go: bool
            use optimized golang minifier if available.

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
        self._app = app
        self.passive = passive
        self.static = static
        self.go = go
        self.cache = MemoryCache(self.get_endpoint, caching_limit)
        self.parser = Parser(parsers, fail_safe, go=go)
        self.parser.update_runtime_options(html, js, cssless, script_types)

        app and self.init_app(app)

    def get_endpoint(self):
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

    @property
    def app(self):
        """If app was passed take it, otherwise fallback to `Flask.current_app`.

        Returns
        -------
        Flask App
            The current Flask application.
        """
        return self._app or current_app

    def init_app(self, app):
        """Handle initiation of multiple apps NOTE:Factory Method"""
        self._app = app
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
        _, bypassed = self.get_endpoint_matches(self.bypass_caching)
        get_minified = lambda: self.parser.minify(content, tag)

        if bypassed:
            return get_minified()

        return self.cache.get_or_set(content, get_minified)

    def get_endpoint_matches(self, patterns):
        """Get the patterns that matches the current endpoint.

        Parameters
        ----------
        patterns: list
            regex patterns or strings to match endpoint.

        Returns
        -------
        (iterable, bool)
            patterns that match the current endpoint, and True if any matches found
        """
        endpoint = self.get_endpoint()
        matches, duplicates = tee(
            p for p in map(compile_re, patterns) if p.search(endpoint)
        )
        has_matches = next(duplicates, 0) != 0

        return matches, has_matches

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
        _, bypassed = self.get_endpoint_matches(self.bypass)
        should_bypass = bypassed or self.passive
        html, cssless, js = does_content_type_match(response)
        should_minify = (
            (html and self.html) or (cssless and self.cssless) or (js and self.js)
        )

        if should_minify and not should_bypass:
            if html or (self.static and (cssless or js)):
                response.direct_passthrough = False
                content = response.get_data(as_text=True)
                tag = "html" if html else "script" if js else "style"
                minified = self.get_minified_or_cached(content, tag)

                response.set_data(minified)

        return response
