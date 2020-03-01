from re import sub, compile as compile_re, DOTALL


def is_empty(content):
    ''' Check if the content is truly empty.

    Paramaters
    ----------
        content: str
            content to check if it's truly empty.

    Returns
    -------
        Boolean True if empty False if not.
    '''
    return not bool(len(sub(r'[ |\n|\t]', '', content or '').strip()))


def get_tag_contents(html, tag):
    ''' Get list of html tag contents.

    Parameters
    ----------
        html: string
            html flask response content.
        tag: string
            tag to retrieve its specific content.

    Returns
    -------
        String of specific tag's inner content.
    '''
    contents = compile_re(r'<{0}[^>]*>(.+?)</{0}>'
                          .format(tag), DOTALL).findall(html)

    return [content for content in contents if not is_empty(content)]


def is_html(response):
    ''' Check if Flask response if of HTML type.

    Parameters
    ----------
        response: Flask response

    Returns
    -------
        True if valid False if not.
    '''
    content_type = getattr(response, 'content_type', '')

    return 'text/html' in content_type.lower()
