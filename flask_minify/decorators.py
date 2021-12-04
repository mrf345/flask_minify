from functools import wraps


def minify(
    html=False,
    js=False,
    cssless=False,
    cache=True,
    fail_safe=True,
    parsers={},
    parser_precedence=False,
):
    """Decorator to minify endpoint HTML output.

    Parameters
    ----------
        html: bool
            enable minifying HTML content.
        js: bool
            enable minifying JavaScript content.
        cssless: bool
            enable minifying CSS/LESS content.
        cache: bool
            enable caching minifed response.
        failsafe: bool
            silence encountered exceptions.
        parsers: dict
            parsers to handle minifying specific tags.
        parser_options_take_precedence: bool
            allow parser specific options to override the extension.

    Returns
    -------
        String of minified HTML content.
    """

    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            from .main import hashing
            from .parsers import Parser

            text = function(*args, **kwargs)
            key = None
            cache_key, cached = function.__dict__.get("minify", (None, None))
            should_minify = isinstance(text, str) and any([html, js, cssless])
            runtime_options = {
                "html": {
                    "only_html_content": not html,
                    "minify_inline": {
                        "script": js,
                        "style": cssless,
                    },
                },
            }

            if should_minify:
                if cache:
                    key = hashing(text).hexdigest()

                if cache_key != key or not cache:
                    parser = Parser(
                        runtime_options=runtime_options,
                        fail_safe=fail_safe,
                        parsers=parsers,
                        parser_precedence=parser_precedence,
                    )
                    text = parser.minify(text, "html")

                    if cache:
                        function.__dict__["minify"] = (key, text)

            should_return_cached = all([cache_key == key, cache, should_minify])
            return cached if should_return_cached else text

        return wrapper

    return decorator
