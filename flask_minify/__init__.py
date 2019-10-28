from sys import maxsize
from six import StringIO
from re import compile as compile_re, DOTALL, sub
from flask import request
from xxhash import xxh64, xxh32
from htmlmin import minify as minify_html
from lesscpy import compile as compile_less
from jsmin import jsmin


class minify(object):
    def __init__(
        self, app=None, html=True, js=True, cssless=True,
        fail_safe=True, bypass=[], cacheing_limit=1
    ):
        '''Flask extension to minify flask response for html, javascript, css and less.

        Parameters:
        ----------
            app: Flask app instance to be passed (default:None).
            js: To minify the css output (default:False).
            cssless: To minify spaces in css (default:True).
            cache: To cache minifed response with hash (default: True).
            fail_safe: to avoid raising error while minifying (default: True).
            caching_limit: to limit the number of minifed response variations.
            (default: 1)

            NOTE: if `caching_limit` is set to 0, we'll not cache any endpoint
                  response, so if you want to disable caching just do that.
        '''
        self.app = app
        self.html = html
        self.js = js
        self.cssless = cssless
        self.fail_safe = fail_safe
        self.bypass = bypass
        self.caching_limit = cacheing_limit
        self.cache = {}

        if not app:
            raise(AttributeError("minify(app=) requires Flask app instance"))
        for arg in ['cssless', 'js', 'html']:
            if not isinstance(eval(arg), bool):
                raise(TypeError("minify(" + arg + "=) requires True or False"))
        self.app.after_request(self.main)

    @property
    def url(self):
        '''to get the current response url.'''
        with self.app.app_context():
            return request.url_rule.rule

    @property
    def hashing(self):
        '''to get appropriate hashing module.'''
        return xxh64 if maxsize > 2**32 else xxh32

    def get_minified(self, content, style):
        '''to minify css/less or javascript and failsafe that.

        Parameters:
            content [str]: a script or style html tag content.
            style [bool]: if the content belongs to a style html tag.
        '''
        try:
            return compile_less(StringIO(content), minify=True, xminify=True)\
                   if style else jsmin(content).replace('\n', ';')
        except Exception as e:
            if self.fail_safe:
                return content
            raise e

    def store_or_restore_cache(self, content, style):
        '''to check if the content is already cached and restore or store it.

        Parameters:
            content [str]: a script or style html tag content.
            style [bool]: if the content belongs to a style html tag.
        '''
        key = self.hashing(content).hexdigest()
        cached = self.cache.get(self.url, {}).get(key)
        should_cache = self.caching_limit > len(self.cache.get(self.url, {}))

        not cached and should_cache and self.cache.setdefault(
            self.url, {}).update({key: self.get_minified(content, style)})

        return self.cache[self.url][key] if cached\
            else self.get_minified(content, style)

    def main(self, response):
        valid_html = response.content_type == u'text/html; charset=utf-8'
        should_bypass = self.url in self.bypass

        if valid_html and not should_bypass:
            response.direct_passthrough = False
            text = response.get_data(as_text=True)
            tags = {'style': self.cssless, 'script': self.js}
            tags_iter = getattr(tags, 'iteritems', tags.items)

            for tag, applicable in tags_iter():
                if applicable:
                    tag_contents = compile_re(
                        r'<{0}[^>]*>(.+?)</{0}>'
                        .format(tag), DOTALL).findall(text)

                    for content in tag_contents:
                        if content and len(sub(r'[ |\n|\t]', '', content)) > 1:
                            text = text.replace(
                                content, self.store_or_restore_cache(
                                    content, tag == 'style'))

            response.set_data(minify_html(text) if self.html else text)
        return response
