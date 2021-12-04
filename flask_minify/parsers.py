from io import StringIO

from htmlmin import minify as minify_html
from jsmin import jsmin
from lesscpy import compile as compile_less
from rcssmin import cssmin

from flask_minify.utils import get_tag_contents


class Jsmin:
    runtime_options = {"quote_chars": "'\"`"}
    executer = staticmethod(jsmin)


class Rcssmin:
    runtime_options = {"keep_bang_comments": False}
    executer = staticmethod(cssmin)


class Lesscpy:
    runtime_options = {"minify": True, "xminify": True}

    def executer(self, content, **options):
        return compile_less(StringIO(content), **options)


class Html:
    _default_tags = {
        "script": False,
        "style": False,
    }
    runtime_options = {
        "remove_comments": True,
        "remove_optional_attribute_quotes": False,
        "only_html_content": False,
        "script_types": [],
        "minify_inline": _default_tags,
    }

    def executer(self, content, **options):
        only_html_content = options.pop("only_html_content", False)
        script_types = options.pop("script_types", [])
        minify_inline = options.pop("minify_inline", self._default_tags)
        enabled_tags = (t for t, e in minify_inline.items() if e)

        for tag in enabled_tags:
            for sub_content in get_tag_contents(content, tag, script_types):
                minified = self.parser.minify(sub_content, tag)
                content = content.replace(sub_content, minified)

        return content if only_html_content else minify_html(content, **options)


class Parser:
    _default_parsers = {"html": Html, "script": Jsmin, "style": Rcssmin}

    def __init__(
        self,
        parsers={},
        runtime_options={},
        fail_safe=False,
        parser_precedence=False,
    ):
        self.parsers = {**self._default_parsers, **parsers}
        self.runtime_options = {**runtime_options}
        self.fail_safe = fail_safe
        self.parser_precedence = parser_precedence

    def minify(self, content, tag):
        if tag not in self.parsers:
            raise KeyError('Unknown tag "{0}"'.format(tag))

        parser = self.parsers[tag]()
        parser.parser = self

        if self.parser_precedence:
            runtime_options = {
                **self.runtime_options.get(tag, {}),
                **parser.runtime_options,
            }
        else:
            runtime_options = {
                **parser.runtime_options,
                **self.runtime_options.get(tag, {}),
            }

        try:
            minified = parser.executer(content, **runtime_options)
        except Exception as e:
            minified = parser.executer(content, **runtime_options)
            if not self.fail_safe:
                raise e
            minified = content

        return minified
