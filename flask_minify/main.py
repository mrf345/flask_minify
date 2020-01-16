from sys import maxsize
from six import StringIO
from re import compile as compile_re, DOTALL
from flask import request, _app_ctx_stack
from xxhash import xxh64, xxh32
from htmlmin import minify as minify_html
from lesscpy import compile as compile_less
from jsmin import jsmin

from flask_minify.utils import is_empty

# optimized hashing speed based on cpu architecture
hashing = xxh64 if maxsize > 2**32 else xxh32


class minify(object):
    def __init__(
        self, app=None, html=True, js=True, cssless=True,
        fail_safe=True, bypass=[], bypass_caching=[], caching_limit=1
    ):
        ''' Extension to minify flask response for html, javascript, css and less.

        Parameters
        ----------
            app: Flask.app
                Flask app instance to be passed.
            js: bool
                To minify the css output.
            cssless: bool
                To minify spaces in css.
            fail_safe: bool
                to avoid raising error while minifying.
            bypass: list
                list of endpoints to bypass minifying for. (Regex)
            bypass_caching: list
                list of endpoints to bypass caching for. (Regex)
            caching_limit: int
                to limit the number of minifed response variations.

            NOTE: if `caching_limit` is set to 0, we'll not cache any endpoint
                  response, so if you want to disable caching just do that.

            EXAMPLE: endpoint is the name of the function decorated with the
                    `@app.route()` so in the following example the endpoint
                    will be `root`:

                     @app.route('/root/<id>')
                     def root(id):
                         return id

            NOTE: when using a `Blueprint` the decorated endpoint will be
                  suffixed with the blueprint name;
                  `Blueprint('blueprint_name')` so here the endpoint will be
                  `blueprint_name.root`.

                  `bypass` and `bypass_caching` can handle regex patterns so if
                  you want to bypass all routes on a certain blueprint you can
                  just pass the pattern as such:
                  minify(app, bypass=['blueprint_name.*'])
        '''
        self.html = html
        self.js = js
        self.cssless = cssless
        self.fail_safe = fail_safe
        self.bypass = bypass
        self.bypass_caching = bypass_caching
        self.caching_limit = caching_limit
        self.cache = {}
        self._app = app

        app and self.init_app(app)

    @property
    def app(self):
        ''' If app was passed take it, if not get the one on top.

        Returns
        -------
            The current Flask application.
        '''
        return self._app or _app_ctx_stack.top

    @property
    def endpoint(self):
        ''' Get the current response endpoint, with a failsafe.

        Returns
        -------
            String of the current endpoint.
        '''
        with self.app.app_context():
            return getattr(request, 'endpoint', '') or ''

    @property
    def iter_tags_to_minify(self):
        ''' Safely iterate html tags to minify, if tag's enabled '''
        tags = {'style': self.cssless, 'script': self.js}

        return getattr(tags, 'iteritems', tags.items)()

    def init_app(self, app):
        ''' Handle initiation of multiple apps NOTE:Factory Method'''
        app.after_request(self.main)
        app.teardown_appcontext(self.teardown)

    def teardown(self, exception):
        ''' Nothing todo on app context teardown XXX:Factory Method'''
        pass

    def get_minified(self, content, style):
        ''' To minify css/less or javascript and failsafe that.

        Parameters
        ----------
            content: str
                a script or style html tag content.
            style: bool
                if the content belongs to a style html tag.

        Returns
        -------
            String of minified passed content.
        '''
        try:
            return compile_less(StringIO(content), minify=True, xminify=True)\
                   if style else jsmin(content).replace('\n', ';')
        except Exception as exception:
            if self.fail_safe:
                return content
            raise exception

    def get_endpoint_matches(self, patterns):
        ''' Get the patterns that matches the current endpoint.

        Parameters
        ----------
            patterns: list
                regex patterns or strings to match endpoint.

        Returns
        -------
            List of patterns that match the current endpoint.
        '''
        matches = [compiled_pattern for compiled_pattern in
                   [compile_re(pattern) for pattern in patterns]
                   if compiled_pattern.match(self.endpoint)]

        return matches

    def store_or_restore_cache(self, content, style):
        ''' Check if the content is already cached and restore or store it.

        Parameters
        ----------
            content: str
                a script or style html tag content.
            style: bool
                if the content belongs to a style html tag.

        Returns
        -------
            Stored or restored minifed content.
        '''
        key = hashing(content).hexdigest()
        should_cache = all([
            not self.get_endpoint_matches(self.bypass_caching),
            self.caching_limit > len(self.cache.get(self.endpoint, {}))])

        def cache():
            return self.cache.get(self.endpoint, {}).get(key)

        if not cache() and should_cache:
            self.cache\
                .setdefault(self.endpoint, {})\
                .update({key: self.get_minified(content, style)})

        return cache() or self.get_minified(content, style)

    def main(self, response):
        ''' Where a dragon once lived!

        Parameters
        ----------
            response: Flask.response
                instance form the `after_request` handler.

        Returns
        -------
            Minified flask response if it fits the requirements.
        '''
        valid_html = response.content_type == u'text/html; charset=utf-8'
        should_bypass = self.get_endpoint_matches(self.bypass)

        if valid_html and not should_bypass:
            response.direct_passthrough = False
            text = response.get_data(as_text=True)

            for tag, enabled in self.iter_tags_to_minify:
                if enabled:
                    tag_contents = compile_re(
                        r'<{0}[^>]*>(.+?)</{0}>'
                        .format(tag), DOTALL).findall(text)

                    for content in tag_contents:
                        if not is_empty(content):
                            text = text.replace(
                                content,
                                self.store_or_restore_cache
                                (content, tag == 'style'))

            response.set_data(minify_html(text) if self.html else text)
        return response
