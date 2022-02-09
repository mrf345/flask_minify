from re import DOTALL
from re import compile as compile_re
from re import sub
from sys import maxsize

from xxhash import xxh32, xxh64


def is_empty(content):
    """Check if the content is truly empty.

    Paramaters
    ----------
        content: str
            content to check if it's truly empty.

    Returns
    -------
        Boolean True if empty False if not.
    """
    return not sub(r"[ |\n|\t]", "", content or "").strip()


def is_valid_tag_content(tag, opening_tag_html, content, script_types):
    """Check if the content is valid for its tag type and definition.

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
    """
    if is_empty(content):
        return False

    if tag == "script" and len(script_types):
        tag_no_quotes = opening_tag_html.replace('"', "").replace("'", "").lower()

        if "" in script_types:
            if "type=" not in tag_no_quotes:
                return True

        valid_types = {
            "type={}".format(script_type)
            for script_type in script_types
            if script_type != ""
        }

        if not any(valid_type in tag_no_quotes for valid_type in valid_types):
            return False

    return True


def get_tag_contents(html, tag, script_types):
    """Get list of html tag contents.

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
    """
    regex = compile_re(r"(<{0}[^>]*>)(.*?)</{0}>".format(tag), DOTALL)

    return (
        content[1]
        for content in regex.findall(html)
        if is_valid_tag_content(tag, content[0], content[1], script_types)
    )


def does_content_type_match(response):
    """Check if Flask response of content-type match HTML, CSS\\LESS or JS.

    Parameters
    ----------
        response: Flask response

    Returns
    -------
        (bool, bool, bool)
            html, cssless, js if content type match.
    """
    content_type = getattr(response, "content_type", "").lower()
    html = "text/html" in content_type
    cssless = "css" in content_type or "less" in content_type
    js = "javascript" in content_type

    return html, cssless, js


def get_optimized_hashing():
    """Gets optimized hashing module based on cpu architecture"""
    return xxh64 if maxsize > 2**32 else xxh32
