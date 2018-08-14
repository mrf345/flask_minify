from lesscpy import compile
from jsmin import jsmin
from six import StringIO
from htmlmin import minify as minifyHtml
from hashlib import md5


class minify(object):
    def __init__(self, app=None,
        html=True, js=False,
        cssless=True, cache=True,
        fail_safe=True):
        """
        A Flask extension to minify flask response for html,
        javascript, css and less.
        @param: app Flask app instance to be passed (default:None).
        @param: js To minify the css output (default:False).
        @param: cssless To minify spaces in css (default:True).
        @param: cache To cache minifed response with hash (default: True).
        @param: fail_safe to avoid raising error while minifying (default True).
        """
        self.app = app
        self.html = html
        self.js = js
        self.cssless = cssless
        self.cache = cache
        self.fail_safe = fail_safe
        self.history = {} # where cache hash and compiled response stored 
        if self.app is None:
            raise(AttributeError("minify(app=) requires Flask app instance"))
        for arg in ['cssless', 'js', 'html', 'cache']:
            if not isinstance(eval(arg), bool):
                raise(TypeError("minify(" + arg + "=) requires True or False"))
        self.app.after_request(self.toLoopTag)


    def toLoopTag(self, response):
        if response.content_type == u'text/html; charset=utf-8':
            response.direct_passthrough = False
            text = response.get_data(as_text=True)
            forHash = md5(text.encode('utf8')).hexdigest()[:9]
            if self.cache and forHash in self.history.keys():
                response.set_data(self.history[forHash])
                return response
            for tag in [t for t in [
                (0, 'style')[self.cssless], 
                (0, 'script')[self.js]
                ] if t != 0]:
                if '<' + tag + ' type=' in text or '<' + tag + '>' in text:
                    for i in range(1, len(text.split('<' + tag))):
                        toReplace = text.split(
                            '<' + tag, i
                        )[i].split(
                            '</' + tag + '>'
                        )[0].split(
                            '>', 1
                        )[1]
                        result = None
                        try:
                            result = text.replace(
                                toReplace,
                                compile(StringIO(toReplace),
                                minify=True, xminify=True
                                ) if tag == 'style' else jsmin(toReplace
                                ).replace('\n', ';')
                            ) if len(toReplace) > 2 else text
                            text = result
                        except Exception as e:
                            if self.fail_safe:
                                text = result or text
                            else:
                                raise e
            finalResp = minifyHtml(text) if self.html else text
            response.set_data(finalResp)
            if self.cache:
                self.history[forHash] = finalResp
        return response
