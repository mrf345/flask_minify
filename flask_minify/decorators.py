from functools import wraps

from flask_minify.parsers import Parser
from flask_minify.utils import get_optimized_hashing


def minify(
    html=False,
    js=False,
    cssless=False,
    cache=True,
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
        failsafe: bool
            silence encountered exceptions.
        parsers: dict
            parsers to handle minifying specific tags.

    Returns
    -------
        String of minified HTML content.
    """
    hashing = get_optimized_hashing()
    parser = Parser(parsers, fail_safe)
    parser.update_runtime_options(html, js, cssless)

    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            text = function(*args, **kwargs)
            key = None
            cache_key, cached = function.__dict__.get("minify", (None, None))
            should_minify = isinstance(text, str) and any([html, js, cssless])

            if should_minify:
                if cache:
                    key = hashing(text).hexdigest()

                if cache_key != key or not cache:
                    text = parser.minify(text, "html")

                    if cache:
                        function.__dict__["minify"] = (key, text)

            should_return_cached = cache_key == key and cache and should_minify
            return cached if should_return_cached else text

        return wrapper

    return decorator
