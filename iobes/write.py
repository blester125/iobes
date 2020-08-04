from operator import attrgetter
from typing import List, Optional, Callable
from iobes import SpanEncoding, Span, TokenFunction, SpanFormat, IOB, BIO, IOBES, BILOU, BMEOW
from iobes.utils import safe_get, extract_type


def sort_spans(spans: List[Span]) -> List[Span]:
    """Sort a list of spans ordered by where they start.

    The idea of ordering for spans is that the earlier in the tags the span
    appears (where the span starts) the earlier it will appear in the sorted
    list of spans.

    Args:
        spans: The spans to sort.

    Returns:
        The spans in sorted order. so the earlier in the tag sequence they start the
        earlier they are in this list.
    """
    return sorted(spans, key=attrgetter("start"))


def make_blanks(spans: List[Span], length: Optional[int] = None, fill: str = TokenFunction.OUTSIDE) -> List[str]:
    """Create a list of outside tags that we can populate with tags generated from spans.

    Args:
        spans: The list of spans that will eventually be used to populate the tags.
        length: A pre-specified length for the list of empty tags.
        fill: The value that will be used to populate the list of tags.

    Returns:
        A list of outside tags.
    """
    length = tags_length_from_spans(spans) if length is None else length
    return [fill for _ in range(length)]


def tags_length_from_spans(spans: List[Span]) -> int:
    """Get the length of the list of tags that would be needed to contain all the spans.

    To get a list of tags that are long enough to contain all the spans we need find
    the tag with the largest end index.

    Args:
        spans: The list of spans we need to contain

    Returns:
        The length of the tag list needed.
    """
    return max(spans, key=attrgetter("end")).end


def make_tag(token_function: str, span_type: str, delimiter: str = "-") -> str:
    """Create a tag from a token function and a span type.

    Args:
        token_function: The token function for the tag, it is the first part of the tag.
        span_type: The type of the span this tag is part of it. It is the second part
            of the tag.
        delimiter: A separator character (or sequence of characters) that separate the
            `token_function` and the `span_type`.

    Returns:
        The created tag.
    """
    return f"{token_function}{delimiter}{span_type}"


def write_tags(spans: List[Span], span_type: SpanEncoding, length: Optional[int] = None):
    tags = make_blanks(spans, length)
    if span_type is SpanEncoding.IOB:
        return write_iob_tags(span, length)
    if span_type is SpanEncoding.BIO:
        return _write_tags(spans, BIO, tags)
    if span_type is SpanEncoding.IOBES:
        return _write_tags(spans, IOBES, tags)
    if span_type is SpanEncoding.BILOU:
        return _write_tags(spans, BILOU, tags)
    if span_type is SpanEncoding.BMEOW or span_type is SpanEncoding.BMEWO:
        return _write_tags(spans, BMEOW, tags)
    if span_type is SpanEncoding.TOKEN:
        return _write_tags(spans, TOKEN, tags)
    raise ValueError(f"Unknown SpanEncoding scheme, got: `{span_type}`")


def write_iob_tags(spans: Span, tags: Optional[List[str]] = None, length: Optional[int] = None) -> List[str]:
    """This is a special case because the IOB tags are contextual."""
    spans = sort_spans(spans)
    tags = make_blanks(spans, length) if tags is None else tags
    if not spans:
        return tags
    # The first span can never start with a `B` because it is first and therefore can't follow a
    # span of the same type.
    for token in spans[0].tokens:
        tags[token] = f"{TokenFunction.INSIDE}-{spans[0].type}"
    for prev, span in zip(spans, spans[1:]):
        for token in span.tokens:
            tags[token] = f"{TokenFunction.INSIDE}-{span.type}"
        if prev.end == span.start and prev.type == span.type:
            tags[span.start] = f"{TokenFunction.BEGIN}-{span.type}"
    return tags


def _write_tags(spans: Span, span_format: SpanFormat, tags: Optional[List[str]] = None, length: Optional[int] = None):
    spans = sort_spans(spans)
    tags = make_blanks(spans, length) if tags is None else tags
    for span in spans:
        if len(span.tokens) == 1:
            tags[span.start] = make_tag(span_format.SINGLE, span.type)
            continue
        tags[span.start] = make_tag(span_format.BEGIN, span.type)
        tags[span.end - 1] = make_tag(span_format.END, span.type)
        for token in span.tokens[1:-1]:
            tags[token] = make_tag(span_format.INSIDE, span.type)
    return tags


def write_bio_tags(spans: Span, tags: Optional[List[str]] = None, length: Optional[int] = None) -> List[str]:
    return _write_tags(spans, BIO, tags, length)


def write_iobes_tags(spans: Span, tags: Optional[List[str]] = None, length: Optional[int] = None) -> List[str]:
    return _write_tags(spans, IOBES, tags, length)


def write_bilou_tags(spans: Span, tags: Optional[List[str]] = None, length: Optional[int] = None) -> List[str]:
    return _write_tags(spans, BILOU, tags, length)


def write_bmeow_tags(spans: Span, tags: Optional[List[str]] = None, length: Optional[int] = None) -> List[str]:
    return _write_tags(spans, BMEOW, tags, length)


write_bmewo_tags = write_bmeow_tags
