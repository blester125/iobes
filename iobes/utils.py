from operator import attrgetter
from typing import List, Union, Any
from iobes import Span, Error


def extract_type(tag: str, sep: str = "-") -> str:
    """Extract the span type from a tag.

    Tags are made of two parts. The second part is the type of the span which
    is specific to the downstream task. This function extracts that value from
    the tag.

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
    in a span. It is generic across datasets (but differs across different span
    formatting options) and tells us things like this tag is the beginning or a
    span or this tag ends a span. This function extracts the token function or
    from the tag.

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
    """Get the element at some index but return ``None`` when the index is out of bounds.

    Args:
        xs: The list to extract from.
        idx: The index to try to pull from.

    Returns:
        The value at ``idx`` or ``None`` if ``idx`` is out of bounds.
    """
    if idx < 0 or idx >= len(xs):
        return None
    return xs[idx]


def sort_spans(spans: List[Span]) -> List[Span]:
    """Sort the list of spans.

    Note:
        The spans are sorted by their starting location and ties broken by their end.
        This tie should never happen because span are not allowed to overlap.

    Args:
        spans: The list of spans to sort.

    Returns:
        The sorted spans.
    """
    return sorted(sorted(spans, key=attrgetter("end")), key=attrgetter("start"))


def sort_errors(errors: List[Error]) -> List[Error]:
    """Sort a list of errors.

    Note:
        The errors are sorted by the location they occur in. In the case a single
        transition causes multiple violations they are sorted by the error type.

    Args:
        errors: The list of errors to sort.

    Returns:
        The sorted errors.
    """
    return sorted(sorted(errors, key=attrgetter("type")), key=attrgetter("location"))
