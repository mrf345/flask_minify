from functools import lru_cache
from io import StringIO

from htmlmin import minify as minify_html
from jsmin import jsmin
from lesscpy import compile as compile_less
from rcssmin import cssmin

try:
    import minify as minify_go
except Exception:
    minify_go = None

from flask_minify.exceptions import FlaskMinifyException
from flask_minify.utils import get_tag_contents


class ParserMixin:
    # parser specific runtime option will take precedence over global
    takes_precedence = False
    go = False

    @property
    def options_changed(self):
        return self._o != self.runtime_options


class Jsmin(ParserMixin):
    runtime_options = _o = {"quote_chars": "'\"`"}
    executer = staticmethod(jsmin)


class Rcssmin(ParserMixin):
    runtime_options = _o = {"keep_bang_comments": False}
    executer = staticmethod(cssmin)


class Lesscpy(ParserMixin):
    runtime_options = _o = {"minify": True, "xminify": True}

    def executer(self, content, **options):
        return compile_less(StringIO(content), **options)


class Html(ParserMixin):
    _default_tags = {
        "script": False,
        "style": False,
    }
    runtime_options = _o = {
        "remove_comments": True,
        "remove_optional_attribute_quotes": False,
        "remove_empty_space": True,
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


class GoParserMixin(ParserMixin):
    go = True
    media_type = "text/html"

    @lru_cache(10)
    def get_all_go_options(self):
        all_options = {}

        for parser in self.parser.parsers.values():
            if parser.go:
                all_options.update(parser.runtime_options)

        return all_options

    def executer(self, content, **options):
        minify_go.config({**self.get_all_go_options(), **options})
        return minify_go.string(self.media_type, content)


class HtmlGo(GoParserMixin):
    runtime_options = _o = {
        "html-keep-comments": False,
        "html-keep-special-comments": True,
        "html-keep-default-attr-vals": True,
        "html-keep-document-tags": True,
        "html-keep-end-tags": True,
        "html-keep-whitespace": False,
        "html-keep-quotes": True,
    }


class JsGo(GoParserMixin):
    media_type = "text/javascript"
    runtime_options = _o = {
        "js-precision": 0,
        "js-keep-var-names": True,
    }


class CssGo(GoParserMixin):
    media_type = "text/css"
    runtime_options = _o = {"css-precision": 0}


class Parser:
    _default_parsers = {"html": Html, "script": Jsmin, "style": Rcssmin}
    _go_default_parsers = {"html": HtmlGo, "script": JsGo, "style": CssGo}

    def __init__(
        self,
        parsers={},
        fail_safe=False,
        runtime_options={},
        go=False,
    ):
        self.go = go
        self.parsers = {**self.default_parsers, **parsers}
        self.runtime_options = {**runtime_options}
        self.fail_safe = fail_safe

        if self.has_go_parser and not minify_go:
            raise FlaskMinifyException(
                f"Cannot use any Go parsers without installing "
                "Go optional dependency: `pip install flask-minify[go]`"
            )

    @property
    def default_parsers(self):
        return (
            self._go_default_parsers if self.go and minify_go else self._default_parsers
        )

    @property
    def has_go_parser(self):
        return any(p.go for p in self.parsers.values())

    def update_runtime_options(
        self, html=False, js=False, cssless=False, script_types=[]
    ):
        if not minify_go or not self.go:
            self.runtime_options.setdefault("html", {}).update(
                {
                    "only_html_content": not html,
                    "script_types": script_types,
                    "minify_inline": {
                        "script": js,
                        "style": cssless,
                    },
                }
            )

    def minify(self, content, tag):
        if tag not in self.parsers:
            raise FlaskMinifyException('Unknown tag "{0}"'.format(tag))

        parser = self.parsers[tag]()
        parser.parser = self

        if parser.options_changed:
            runtime_options = parser.runtime_options
        elif parser.takes_precedence:
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
            minified_or_content = parser.executer(content, **runtime_options)
        except Exception as e:
            if not self.fail_safe:
                raise FlaskMinifyException(
                    'Failed to minify "{0}" content'.format(tag)
                ) from e

            minified_or_content = content

        return minified_or_content
