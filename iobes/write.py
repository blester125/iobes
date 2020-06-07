from operator import attrgetter
from typing import List, Optional, Callable
from iobes import SpanEncoding, Span, TokenFunction
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
    single_tag: Callable[[str], str],
    start_tag: Callable[[str], str],
    end_tag: Callable[[str], str],
    inside_tag: Callable[[str], str],
    length: Optional[int] = None,
):
    spans = sort_spans(spans)
    tags = make_blanks(spans, length)
    for span in spans:
        if len(span.tokens) == 1:
            tags[span.start] = single_tag(span.type)
            continue
        tags[span.start] = start_tag(span.type)
        tags[span.end - 1] = end_tag(span.type)
        for token in span.tokens[1:-1]:
            tags[token] = inside_tag(span.type)
    return tags


def write_bio_tags(spans: Span, length: Optional[int] = None) -> List[str]:
    return _write_tags(spans, bio_single_tag, bio_start_tag, bio_end_tag, bio_inside_tag, length)


def write_iobes_tags(spans: Span, length: Optional[int] = None) -> List[str]:
    return _write_tags(spans, iobes_single_tag, iobes_start_tag, iobes_end_tag, iobes_inside_tag, length)


def write_bilou_tags(spans: Span, length: Optional[int] = None) -> List[str]:
    return _write_tags(spans, bilou_single_tag, bilou_start_tag, bilou_end_tag, bilou_inside_tag, length)


def write_bmeow_tags(spans: Span, length: Optional[int] = None) -> List[str]:
    return _write_tags(spans, bmeow_single_tag, bmeow_start_tag, bmeow_end_tag, bmeow_inside_tag, length)


write_bmewo_tags = write_bmeow_tags


def _make_tag(prefix: str, span_type: str, delimiter: str = "-") -> str:
    return f"{prefix}{delimiter}{span_type}"


def iobes_start_tag(span_type: str) -> str:
    return _make_tag(TokenFunction.BEGIN, span_type)


def iobes_inside_tag(span_type: str) -> str:
    return _make_tag(TokenFunction.INSIDE, span_type)


def iobes_end_tag(span_type: str) -> str:
    return _make_tag(TokenFunction.END, span_type)


def iobes_single_tag(span_type: str) -> str:
    return _make_tag(TokenFunction.SINGLE, span_type)


def bio_start_tag(span_type: str) -> str:
    return _make_tag(TokenFunction.BEGIN, span_type)


def bio_inside_tag(span_type: str) -> str:
    return _make_tag(TokenFunction.INSIDE, span_type)


def bio_end_tag(span_type: str) -> str:
    return _make_tag(TokenFunction.INSIDE, span_type)


def bio_single_tag(span_type: str) -> str:
    return _make_tag(TokenFunction.BEGIN, span_type)


def bilou_start_tag(span_type: str) -> str:
    return _make_tag(TokenFunction.BEGIN, span_type)


def bilou_inside_tag(span_type: str) -> str:
    return _make_tag(TokenFunction.INSIDE, span_type)


def bilou_end_tag(span_type: str) -> str:
    return _make_tag(TokenFunction.LAST, span_type)


def bilou_single_tag(span_type: str) -> str:
    return _make_tag(TokenFunction.UNIT, span_type)


def bmeow_start_tag(span_type: str) -> str:
    return _make_tag(TokenFunction.BEGIN, span_type)


def bmeow_inside_tag(span_type: str) -> str:
    return _make_tag(TokenFunction.MIDDLE, span_type)


def bmeow_end_tag(span_type: str) -> str:
    return _make_tag(TokenFunction.END, span_type)


def bmeow_single_tag(span_type: str) -> str:
    return _make_tag(TokenFunction.WHOLE, span_type)


bmewo_start_tag = bmeow_start_tag
bmewo_end_tag = bmeow_end_tag
bmewo_inside_tag = bmeow_inside_tag
bmewo_single_tag = bmeow_single_tag
