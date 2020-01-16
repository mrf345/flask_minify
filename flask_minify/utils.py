from re import sub


def is_empty(content):
    ''' check if the content is truly empty.

    Paramaters
    ----------
        content: str
            content to check if it's truly empty.

    Returns
    -------
        Boolean True if empty False if not.
    '''
    return not bool(len(sub(r'[ |\n|\t]', '', content or '').strip()))
