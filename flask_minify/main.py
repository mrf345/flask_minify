from sys import maxsize
from six import StringIO
from re import compile as compile_re
from flask import request, _app_ctx_stack
from xxhash import xxh64, xxh32
from htmlmin import minify as minify_html
from lesscpy import compile as compile_less
from jsmin import jsmin

from flask_minify.utils import (get_tag_contents, is_html, is_cssless, is_js,
                                iter_tags_to_minify)


# optimized hashing speed based on cpu architecture
hashing = xxh64 if maxsize > 2**32 else xxh32


class Minify(object):
    'Extension to minify flask response for html, javascript, css and less.'

    def __init__(
        self, app=None, html=True, js=True, cssless=True,
        fail_safe=True, bypass=[], bypass_caching=[], caching_limit=2,
        passive=False, static=True, script_types=[]
    ):
        ''' Extension to minify flask response for html, javascript, css and less.

        Parameters
        ----------
        app: Flask.app
            Flask app instance to be passed.
        js: bool
            To minify the js output.
        cssless: bool
            To minify spaces in css.
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
        '''
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

        app and self.init_app(app)

    @property
    def app(self):
        ''' If app was passed take it, if not get the one on top.

        Returns
        -------
        Flask App
            The current Flask application.
        '''
        return self._app or (_app_ctx_stack.top and _app_ctx_stack.top.app)

    @property
    def endpoint(self):
        ''' Get the current response endpoint, with a failsafe.

        Returns
        -------
        str
            the current endpoint.
        '''
        with self.app.app_context():
            path = getattr(request, 'endpoint', '') or ''

            if path == 'static':
                path = getattr(request, 'path', '') or ''

            return path

    def init_app(self, app):
        ''' Handle initiation of multiple apps NOTE:Factory Method'''
        app.after_request(self.main)
        app.teardown_appcontext(self.teardown)

    def teardown(self, exception):
        ''' Nothing todo on app context teardown XXX:Factory Method'''
        pass

    @classmethod
    def get_minified(cls, content, tag, fail_safe=False,
                     only_html_content=False, html_cssless=False,
                     html_js=False, script_types=[]):
        ''' To minify css/less or javascript and failsafe that.

        Parameters
        ----------
        content: str
            a script or style html tag content.
        style: bool
            if the content belongs to a style html tag.
        failsafe: bool
            to avoid raising error while minifying.
        only_html_content: bool
            to skip minifying the HTML tag and just minify its content.
        html_cssless: bool
            to minify html inner css/less.
        html_js: bool
            to minify html inner js.
        script_types: list
            list of script types to limit js minification to.

        Returns
        -------
        str
            minified passed content.
        '''
        try:
            if tag == 'style':
                return compile_less(StringIO(content),
                                    minify=True,
                                    xminify=True)
            elif tag == 'script':
                return jsmin(content,
                             quote_chars="'\"`").replace('\n', ';')
            elif tag == 'html':
                for tag, enabled in iter_tags_to_minify(html_cssless,
                                                        html_js):
                    if enabled:
                        for sub_content in get_tag_contents(content,
                                                            tag,
                                                            script_types):
                            content = content.replace(sub_content,
                                                      cls.get_minified(
                                                          sub_content,
                                                          tag,
                                                          fail_safe,
                                                          script_types))

                return content if only_html_content else minify_html(
                    content,
                    remove_comments=True,
                    remove_optional_attribute_quotes=False)
            else:
                raise AttributeError('Unknown HTML tag')

        except Exception as exception:
            if fail_safe:
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
        list
            patterns that match the current endpoint.
        '''
        matches = [compiled_pattern for compiled_pattern in
                   [compile_re(pattern) for pattern in patterns]
                   if compiled_pattern.search(self.endpoint)]

        return matches

    def get_minified_or_cached(self, content, tag):
        ''' Check if the content is already cached and restore or store it.

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
        '''
        def _cache_dict():
            return self.cache.get(self.endpoint, {})

        key = hashing(content).hexdigest()
        bypassed = bool(self.get_endpoint_matches(self.bypass_caching))
        limit_reached = len(_cache_dict()) >= self.caching_limit

        def _cached():
            return _cache_dict().get(key)

        def _minified():
            return self.get_minified(content,
                                     tag,
                                     self.fail_safe,
                                     not self.html,
                                     self.cssless,
                                     self.js,
                                     self.script_types)

        if not _cached() and not bypassed:
            if limit_reached and _cache_dict():
                _cache_dict().popitem()

            self.cache\
                .setdefault(self.endpoint, {})\
                .update({key: _minified()})

        return _cached() or _minified()

    def main(self, response):
        ''' Where a dragon once lived!

        Parameters
        ----------
        response: Flask.response
            instance form the `after_request` handler.

        Returns
        -------
        Flask.Response
            minified flask response if it fits the requirements.
        '''
        html = is_html(response)
        cssless = is_cssless(response)
        js = is_js(response)
        should_minify = any([html and self.html,
                             cssless and self.cssless,
                             js and self.js])
        should_bypass = bool(self.get_endpoint_matches(self.bypass)
                             or self.passive)

        if should_minify and not should_bypass:
            response.direct_passthrough = False
            text = response.get_data(as_text=True)

            if html or (self.static and any([cssless, js])):
                response.set_data(
                    self.get_minified_or_cached(text,
                                                'html' if html else
                                                'script' if js else 'style'))

        return response
