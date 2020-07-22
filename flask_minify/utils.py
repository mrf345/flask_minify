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


def is_valid_tag_content(tag, opening_tag_html, content, script_types):
    ''' Check if the content is valid for its tag type and definition.

    Paramaters
    ----------
        tag: str
            the tag type to validate.
        opening_tag_html: str
            the html of the opening tag, including any attributes.
        content: str
            content to check if it's empty.
        script_types: list
            list of script types to limit js minification to.

    Returns
    -------
        Boolean True if valid, False if not.
    '''
    if is_empty(content):
        return False

    if tag == 'script' and len(script_types):
        tag_no_quotes = opening_tag_html.replace('"', '')\
                                        .replace("'", '')\
                                        .lower()

        if '' in script_types:
            if 'type=' not in tag_no_quotes:
                return True

        valid_types = ['type={}'.format(script_type)
                       for script_type in script_types if script_type != '']

        if not any(valid_type in tag_no_quotes for valid_type in valid_types):
            return False

    return True


def get_tag_contents(html, tag, script_types):
    ''' Get list of html tag contents.

    Parameters
    ----------
        html: string
            html flask response content.
        tag: string
            tag to retrieve its specific content.
        script_types: list
            list of script types to limit js minification to.

    Returns
    -------
        String of specific tag's inner content.
    '''
    contents = compile_re(r'(<{0}[^>]*>)(.*?)</{0}>'
                          .format(tag), DOTALL).findall(html)

    return [content[1] for content in contents
            if is_valid_tag_content(tag, content[0], content[1], script_types)]


def is_html(response):
    ''' Check if Flask response of HTML content-type.

    Parameters
    ----------
        response: Flask response

    Returns
    -------
        True if valid False if not.
    '''
    content_type = getattr(response, 'content_type', '')

    return 'text/html' in content_type.lower()


def is_js(response):
    ''' Check if Flask response of JS content-type.

    Parameters
    ----------
        response: Flask response

    Returns
    -------
        True if valid False if not.
    '''
    content_type = getattr(response, 'content_type', '')

    return 'javascript' in content_type.lower()


def is_cssless(response):
    ''' Check if Flask response of Css or Less content-type.

    Parameters
    ----------
        response: Flask response

    Returns
    -------
        True if valid False if not.
    '''
    content_type = getattr(response, 'content_type', '')

    return 'css' in content_type.lower() or 'less' in content_type.lower()


def iter_tags_to_minify(cssless, js):
    ''' Safely iterate html tags to minify, if tag's enabled.
    Parameters
    ----------
    cssless: bool
        to enable css and less.
    js: bool
        to enable javascript.
    Returns
    -------
    list
        html's tag and its status.
    '''
    tags = {'style': cssless, 'script': js}

    return getattr(tags, 'iteritems', tags.items)()
