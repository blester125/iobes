from operator import attrgetter
from typing import List, Optional, Callable
from iobes import SpanEncoding, Span, TokenFunction, SpanFormat, IOB, BIO, IOBES, BILOU, BMEOW
from iobes.utils import safe_get, extract_type


def to_tags(spans: List[Span], span_type: SpanEncoding, length: Optional[int] = None) -> List[str]:
    length = max(spans, key=attrgetter("end")).end if length is None else length
    tags = [TokenFunction.OUTSIDE for _ in range(length)]
    for span in spans:
        tags = write_tags(span, tags, span_type)
    return tags


def sort_spans(spans: List[Span]) -> List[Span]:
    return sorted(spans, key=attrgetter("start"))


def make_blanks(spans, length: Optional[int] = None, fill: str = TokenFunction.OUTSIDE) -> List[str]:
    length = max(spans, key=attrgetter("end")).end if length is None else length
    return [fill for _ in range(length)]


def write_tags(span: Span, tags: List[str], span_type: SpanEncoding):
    if span_type is SpanEncoding.IOB:
        return write_iob_tags(span, tags)
    if span_type is SpanEncoding.BIO:
        return write_bio_tags(span, tags)
    if span_type is SpanEncoding.IOBES:
        return write_iobes_tags(span, tags)
    if span_type is SpanEncoding.BILOU:
        return write_bilou_tags(span, tags)
    if span_type is SpanEncoding.BMEOW or span_type is SpanEncoding.BMEWO:
        return write_bmeow_tags(span, tags)
    raise ValueError(f"Unknown SpanEncoding scheme, got: `{span_type}`")


def write_iob_tags(spans: Span, length: Optional[int] = None) -> List[str]:
    spans = sort_spans(spans)
    tags = make_blanks(spans, length)
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


def _write_tags(
    spans: Span,
    span_format: SpanFormat,
    length: Optional[int] = None,
):
    spans = sort_spans(spans)
    tags = make_blanks(spans, length)
    for span in spans:
        if len(span.tokens) == 1:
            tags[span.start] = _make_tag(span_format.SINGLE, span.type)
            continue
        tags[span.start] = _make_tag(span_format.BEGIN, span.type)
        tags[span.end - 1] = _make_tag(span_format.END, span.type)
        for token in span.tokens[1:-1]:
            tags[token] = _make_tag(span_format.INSIDE, span.type)
    return tags


def write_bio_tags(spans: Span, length: Optional[int] = None) -> List[str]:
    return _write_tags(spans, BIO, length)


def write_iobes_tags(spans: Span, length: Optional[int] = None) -> List[str]:
    return _write_tags(spans, IOBES, length)


def write_bilou_tags(spans: Span, length: Optional[int] = None) -> List[str]:
    return _write_tags(spans, BILOU, length)


def write_bmeow_tags(spans: Span, length: Optional[int] = None) -> List[str]:
    return _write_tags(spans, BMEOW, length)


write_bmewo_tags = write_bmeow_tags


def _make_tag(prefix: str, span_type: str, delimiter: str = "-") -> str:
    return f"{prefix}{delimiter}{span_type}"
