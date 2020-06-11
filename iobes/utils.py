from typing import List, Union, Any


def extract_type(tag: str, sep: str = "-") -> str:
    """Extract the span type from a tag.

    Tags are made of two parts. The second part is the type of the span which
    is specific to the downstream task. This function extracts this value from
    a tag.

    Args:
        tag: The tag to extract the type from.
        sep: The character (or string of characters) that separate the token
            function from the span type.

    Returns:
        The span type.
    """
    if sep not in tag:
        return tag
    return tag.split(sep, maxsplit=1)[1]


def extract_function(tag: str, sep: str = "-") -> str:
    """Extract the token function from a tag.

    Tags are made of two parts. The first part is the role that this tag plays
    in a span. It is generic across datasets and tells us things like this tag
    is the beginning or a span or this tag ends a span. This function extracts
    this token function or role from the tag.

    Args:
        tag: The tag to extract the token function from.
        sep: The character (or string of characters) that separate the token
            function from the span type.

    Returns:
        The token function of this tag.
    """
    if sep not in tag:
        return tag
    return tag.split(sep, maxsplit=1)[0]


def safe_get(xs: List[Any], idx: int) -> Union[Any, None]:
    """Get the element at some index but return `None` when the index is out of bounds.

    Args:
        xs: The list to extract from.
        idx: The index to try to pull from.

    Returns:
        The value at `idx` or None if `idx` is out of bounds.
    """
    if idx < 0 or idx >= len(xs):
        return None
    return xs[idx]
