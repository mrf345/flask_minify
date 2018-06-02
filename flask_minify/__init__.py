from os import remove, path, name as osName
from lesscpy import compile
from jsmin import jsmin
from six import StringIO
from htmlmin import minify as minifyHtml


class minify(object):
    def __init__(self, app=None, html=True, js=False, cssless=True):
        """
        A Flask extension to minify flask response for html,
        javascript, css and less.
        @param: app Flask app instance to be passed (default:None).
        @param: js To minify the css output (default:False).
        @param: cssless To minify spaces in css (default:True).
        """
        self.app = app
        self.html = html
        self.js = js
        self.cssless = cssless
        self.tags = []
        if self.js:
            self.tags.append('script')
        if self.cssless:
            self.tags.append('style')
        if self.app is None:
            raise(AttributeError("minify(app=) requires Flask app instance"))
        for arg in [
            ['cssless', cssless],
            ['js', js]]:
            if not isinstance(arg[1], bool):
                raise(TypeError("minify(" + arg[0] + "=) requires True or False"))
        app.after_request(self.toLoopTag)


    def toLoopTag(self, response):
        if response.content_type == u'text/html; charset=utf-8':
            response.direct_passthrough = False
            text = response.get_data(as_text=True)
            for tag in self.tags:
                if '<' + tag + ' type=' in text or '<' + tag + '>' in text:
                    for i in range(1, len(text.split('<' + tag))):
                        toReplace = text.split('<' + tag, i)[i].split('</' + tag + '>')[0]
                        toReplace = toReplace.split('>', 1)[1]
                        if tag == 'style':
                            text = text.replace(toReplace, compile(StringIO(toReplace), minify=True, xminify=True))
                        elif tag == 'script':
                            text = text.replace(toReplace, jsmin(toReplace).replace('\n', ';'))
            if self.html:
                response.set_data(minifyHtml(text))
            else:
                response.set_data(text)
        return response
