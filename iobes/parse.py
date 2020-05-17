from typing import List, Tuple
from iobes import Span, Encoding, Error, Function
from iobes.utils import extract_function, extract_type
from iobes.convert import bilou_to_iobes, bmeow_to_iobes


def parse_spans(seq: List[str], span_type: Encoding) -> List[Span]:
    return parse_spans_with_errors(seq, span_type)[0]


def parse_spans_with_errors(seq: List[str], span_type: Encoding) -> Tuple[List[Span], List[Error]]:
    if span_type is Encoding.IOB:
        return parse_spans_iob_with_errors(seq)
    if span_type is Encoding.BIO:
        return parse_spans_bio_with_errors(seq)
    if span_type is Encoding.IOBES:
        return parse_spans_iobes_with_errors(seq)
    if span_type is Encoding.BILOU:
        return parse_spans_bilou_with_errors(seq)
    if span_type is Encoding.BMEWO:
        return parse_spans_bmewo_with_errors(seq)
    if span_type is Encoding.TOKEN:
        return parse_spans_token_with_errors(seq)
    raise ValueError(f"Unknown Encoding Scheme, got: `{span_type}`")


def parse_spans_token(seq: List[str]) -> List[Span]:
    return parse_spans_token_with_errors(seq)[0]


def parse_spans_token_with_errors(seq: List[str]) -> Tuple[List[Span], List[Error]]:
    return [Span(type=t, start=i, end=i + 1, tokens=[i]) for i, t in enumerate(seq)], []


def parse_spans_iob(seq: List[str]) -> List[Span]:
    return parse_spans_iob_with_errors(seq)[0]


def parse_spans_iob_with_errors(seq: List[str]) -> Tuple[List[Span], List[Error]]:
    spans = []
    span = None
    tokens = []
    for i, s in enumerate(seq):
        func = extract_function(s)
        _type = extract_type(s)
        if func != Function.INSIDE and _type != Function.OUTSIDE:
            if span is not None:
                spans.append(Span(span, start=tokens[0], end=tokens[-1] + 1, tokens=tokens))
            span = _type
            tokens = [i]
        elif func == Function.INSIDE:
            if span is not None:
                if span == _type:
                    tokens.append(i)
                else:
                    spans.append(Span(span, start=tokens[0], end=tokens[-1] + 1, tokens=tokens))
                    span = _type
                    tokens = [i]
            else:
                span = _type
                tokens = [i]
        else:
            if span is not None:
                spans.append(Span(span, start=tokens[0], end=tokens[-1] + 1, tokens=tokens))
            span = None
            tokens = []
    if span is not None:
        spans.append(Span(span, start=tokens[0], end=tokens[-1] + 1, tokens=tokens))
    return spans, []


def parse_spans_bio(seq: List[str]) -> List[Span]:
    return parse_spans_bio_with_errors(seq)[0]


def parse_spans_bio_with_errors(seq: List[str]) -> Tuple[List[Span], List[Error]]:
    spans = []
    span = None
    tokens = []
    for i, s in enumerate(seq):
        func = extract_function(s)
        _type = extract_type(s)
        if func != Function.INSIDE and _type != Function.OUTSIDE:
            if span is not None:
                spans.append(Span(span, start=tokens[0], end=tokens[-1] + 1, tokens=tokens))
            span = _type
            tokens = [i]
        elif func == Function.INSIDE:
            if span is not None:
                if span == _type:
                    tokens.append(i)
                else:
                    spans.append(Span(span, start=tokens[0], end=tokens[-1] + 1, tokens=tokens))
                    span = _type
                    tokens = [i]
            else:
                span = _type
                tokens = [i]
        else:
            if span is not None:
                spans.append(Span(span, start=tokens[0], end=tokens[-1] + 1, tokens=tokens))
            span = None
            tokens = []
    if span is not None:
        spans.append(Span(span, start=tokens[0], end=tokens[-1] + 1, tokens=tokens))
    return spans, []


def parse_spans_iobes(seq: List[str]) -> List[Span]:
    return parse_spans_iobes_with_errors(seq)[0]


def parse_spans_iobes_with_errors(seq: List[str]) -> Tuple[List[Span], List[Error]]:
    spans = []
    span = None
    tokens = []
    for i, s in enumerate(seq):
        func = extract_function(s)
        _type = extract_type(s)
        if func == Function.BEGIN:
            if span is not None:
                spans.append(Span(span, start=tokens[0], end=tokens[-1] + 1, tokens=tokens))
            span = _type
            tokens = [i]
            # Look for errors, Single B and last B
        elif func == Function.SINGLE:
            if span is not None:
                # Error because the S is cutting an entity
                spans.append(Span(span, start=tokens[0], end=tokens[-1] + 1, tokens=tokens))
            spans.append(Span(_type, start=i, end=i + 1, tokens=[i]))
            span = None
            tokens = []
        elif func == Function.INSIDE:
            if span is not None:
                if _type == span:
                    tokens.append(i)
                else:
                    # Error because type mismatch
                    spans.append(Span(span, start=tokens[0], end=tokens[-1] + 1, tokens=tokens))
                    span = _type
                    tokens = [i]
            else:
                # Error because start with i
                span = _type
                tokens = [i]
            # Check for final tokens i error
        elif func == Function.END:
            if span is not None:
                if _type == span:
                    tokens.append(i)
                    spans.append(Span(span, start=tokens[0], end=tokens[-1] + 1, tokens=tokens))
                    span = None
                    tokens = []
                else:
                    # Error from type mismatch
                    # Create and end a span with this E-
                    spans.append(Span(_type, start=i, end=i + 1, tokens=[i]))
                    span = None
                    tokens = []
            else:
                # Error because E starts it
                spans.append(Span(_type, start=i, end=i + 1, tokens=[i]))
                span = None
                tokens = []
        else:
            # Error because O cuts it off
            if span is not None:
                spans.append(Span(span, start=tokens[0], end=tokens[-1] + 1, tokens=tokens))
                span = None
                tokens = []
    if span is not None:
        # Error because entity cut off by end of seq
        spans.append(Span(span, start=tokens[0], end=tokens[-1] + 1, tokens=tokens))
        span = None
        tokens = []
    return spans, []


def parse_spans_bilou(seq: List[str]) -> List[Span]:
    return parse_spans_iobes(bilou_to_iobes(seq))


def parse_spans_bilou_with_errors(seq: List[str]) -> Tuple[List[Span], List[Error]]:
    spans, errors = parse_spans_iobes_with_errors(bilou_to_iobes(seq))
    errors = [_convert_error(e) for e in errors]
    return spans, errors


def parse_spans_bmewo(seq: List[str]) -> List[Span]:
    return parse_spans_iobes(bmeow_to_iobes(seq))


def parse_spans_bmewo_with_errors(seq: List[str]) -> Tuple[List[Span], List[Error]]:
    spans, errors = parse_spans_iobes_with_errors(bmeow_to_iobes(seq))
    errors = [_convert_error(e) for e in errors]
    return spans, errors
