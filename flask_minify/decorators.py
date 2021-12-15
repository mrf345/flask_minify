from functools import wraps

from flask_minify.cache import MemoryCache
from flask_minify.parsers import Parser


def minify(
    html=False,
    js=False,
    cssless=False,
    cache=True,
    caching_limit=2,
    fail_safe=True,
    parsers={},
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
        caching_limit: int
            to limit the number of minified response variations.
        failsafe: bool
            silence encountered exceptions.
        parsers: dict
            parsers to handle minifying specific tags.

    Returns
    -------
        String of minified HTML content.
    """
    caching = MemoryCache(caching_limit if cache else 0)
    parser = Parser(parsers, fail_safe)
    parser.update_runtime_options(html, js, cssless)

    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            content = function(*args, **kwargs)
            should_minify = isinstance(content, str) and any([html, js, cssless])
            get_minified = lambda: parser.minify(content, "html")

            if not should_minify:
                return content

            return caching.get_or_set(content, get_minified)

        return wrapper

    return decorator
