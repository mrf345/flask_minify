from functools import wraps

from .main import hashing, Minify as main


def minify(html=False, js=False, cssless=False, cache=True, fail_safe=True):
    ''' Decorator to minify endpoint HTML output.

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

    Returns
    -------
        String of minified HTML content.
    '''
    def wrapper(function):
        @wraps(function)
        def decorator(*args, **kwargs):
            response_text = function(*args, **kwargs)
            text = response_text
            key = None
            cache_key, cached = function.__dict__.get('minify', (None, None))
            should_minify = isinstance(text, str) and any([html, js, cssless])

            if should_minify:
                if cache:
                    key = hashing(text).hexdigest()

                if cache_key != key or not cache:
                    text = main.get_minified(text, 'html', fail_safe,
                                             not html, cssless, js)

                    if cache:
                        function.__dict__['minify'] = (hashing(response_text)
                                                       .hexdigest(), text)

            return cache if all([cache_key == key,
                                 cache,
                                 should_minify]) else text
        return decorator
    return wrapper
