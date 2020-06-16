from typing import List, Tuple, Callable
from iobes import Span, SpanEncoding, SpanFormat, Error, TokenFunction, LOGGER, IOB, BIO, IOBES, BILOU, BMEOW
from iobes.utils import extract_function, extract_type, safe_get


def parse_spans(seq: List[str], span_type: SpanEncoding) -> List[Span]:
    return parse_spans_with_errors(seq, span_type)[0]


def parse_spans_with_errors(seq: List[str], span_type: SpanEncoding) -> Tuple[List[Span], List[Error]]:
    if span_type is SpanEncoding.IOB:
        return parse_spans_iob_with_errors(seq)
    if span_type is SpanEncoding.BIO:
        return parse_spans_bio_with_errors(seq)
    if span_type is SpanEncoding.IOBES:
        return parse_spans_iobes_with_errors(seq)
    if span_type is SpanEncoding.BILOU:
        return parse_spans_bilou_with_errors(seq)
    if span_type is SpanEncoding.BMEOW or span_type is SpanEncoding.BMEWO:
        return parse_spans_bmeow_with_errors(seq)
    if span_type is SpanEncoding.TOKEN:
        return parse_spans_token_with_errors(seq)
    raise ValueError(f"Unknown SpanEncoding scheme, got: `{span_type}`")


def parse_spans_token(seq: List[str]) -> List[Span]:
    return parse_spans_token_with_errors(seq)[0]


def parse_spans_token_with_errors(seq: List[str]) -> Tuple[List[Span], List[Error]]:
    return [Span(type=t, start=i, end=i + 1, tokens=(i,)) for i, t in enumerate(seq)], []


def parse_spans_iob(seq: List[str]) -> List[Span]:
    return parse_spans_iob_with_errors(seq)[0]


def parse_spans_iob_with_errors(seq: List[str]) -> Tuple[List[Span], List[Error]]:
    errors = []
    spans = []
    # This tracks the type of the span we are currently building
    span = None
    # This tracks the tokens that make up the span we are building
    tokens = []
    for i, s in enumerate(seq):
        func = extract_function(s)
        _type = extract_type(s)
        # A `B` ends a current span but starts a new one
        if func == TokenFunction.BEGIN:
            prev_type = extract_type(seq[i - 1]) if i > 0 else None
            # In `iob` `B` is only allowed to mark the boundary between to spans of the same type that touch
            # `B` isn't allowed to arbitrary start and entity which would happen when `B` is the first token
            # or the last token was an outside
            if i == 0 or prev_type == TokenFunction.OUTSIDE:
                LOGGER.warning("Invalid label: `B` starting an entity at %d", i)
                errors.append(Error(i, "Illegal Start", s, safe_get(seq, i - 1), safe_get(seq, i + 1)))
            # If the previous type isn't the same as our type we should have just used an `I` to transition
            elif prev_type != _type:
                LOGGER.warning("Invalid label: `B` starting and entity after a %s at %d", prev_type, i)
                errors.append(Error(i, "Illegal Transition", s, safe_get(seq, i - 1), safe_get(seq, i + 1)))
            # If there is a span getting built save it out.
            if span is not None:
                spans.append(Span(span, start=tokens[0], end=tokens[-1] + 1, tokens=tuple(tokens)))
            # Create a new span starting with this B
            span = _type
            tokens = [i]
        # An `I` will continue a span when the types match and force a new one otherwise
        elif func == TokenFunction.INSIDE:
            # There is already a span being build
            if span is not None:
                # If we match types are are a continuation of that span
                if span == _type:
                    tokens.append(i)
                # If we don't match types then we are starting a new span. Save old and start a new one.
                else:
                    spans.append(Span(span, start=tokens[0], end=tokens[-1] + 1, tokens=tuple(tokens)))
                    span = _type
                    tokens = [i]
            # This I starts a new entity
            else:
                span = _type
                tokens = [i]
        # An `O` will end an entity being built
        else:
            # If a span was being made cut it here and save the span out.
            if span is not None:
                spans.append(Span(span, start=tokens[0], end=tokens[-1] + 1, tokens=tuple(tokens)))
            span = None
            tokens = []
    # If we fell off the end save the span that was being made
    if span is not None:
        spans.append(Span(span, start=tokens[0], end=tokens[-1] + 1, tokens=tuple(tokens)))
    return spans, errors


def parse_spans_bio(seq: List[str]) -> List[Span]:
    return parse_spans_bio_with_errors(seq)[0]


def parse_spans_bio_with_errors(seq: List[str]) -> Tuple[List[Span], List[Error]]:
    errors = []
    spans = []
    # This tracks the type of the span we are building out
    span = None
    # This tracks the tokens of the span we are building out
    tokens = []
    for i, s in enumerate(seq):
        func = extract_function(s)
        _type = extract_type(s)
        # A `B` ends a span and starts a new one
        if func == BIO.BEGIN:
            # Save out the old span
            if span is not None:
                spans.append(Span(span, start=tokens[0], end=tokens[-1] + 1, tokens=tuple(tokens)))
            # Start the new span
            span = _type
            tokens = [i]
        # An `I` will continue a span when types match and start a new one otherwise.
        elif func == BIO.INSIDE:
            # A span is already being built
            if span is not None:
                # The types match so we just add to the current span
                if span == _type:
                    tokens.append(i)
                # Types mismatch so create a new span
                else:
                    # Log error from type mismatch
                    LOGGER.warning("Illegal Label: I doesn't match previous token at %d", i)
                    errors.append(Error(i, "Illegal Transition", s, safe_get(seq, i - 1), safe_get(seq, i + 1)))
                    # Save out the previous span
                    spans.append(Span(span, start=tokens[0], end=tokens[-1] + 1, tokens=tuple(tokens)))
                    # Start a new span
                    span = _type
                    tokens = [i]
            # No span was being build so start a new one with this I
            else:
                # Log error from starting with I
                LOGGER.warning("Illegal Label: starting a span with `I` at %d", i)
                errors.append(Error(i, "Illegal Start", s, safe_get(seq, i - 1), safe_get(seq, i + 1)))
                span = _type
                tokens = [i]
        # An `O` will cut off a span being built out.
        else:
            if span is not None:
                spans.append(Span(span, start=tokens[0], end=tokens[-1] + 1, tokens=tuple(tokens)))
            # Set so no span is being built
            span = None
            tokens = []
    # If we fell off the end so save the entity that we were making.
    if span is not None:
        spans.append(Span(span, start=tokens[0], end=tokens[-1] + 1, tokens=tuple(tokens)))
    return spans, errors


def parse_spans_with_end(seq: List[str], span_format: SpanFormat) -> List[Span]:
    return parse_spans_with_end_with_errors(seq, span_format)[0]


def parse_spans_with_end_with_errors(seq: List[str], span_format: SpanFormat) -> Tuple[List[Span], List[Error]]:
    errors = []
    spans = []
    # The type of the span we are building
    span = None
    # The tokens of the span we are building
    tokens = []
    for i, s in enumerate(seq):
        func = extract_function(s)
        _type = extract_type(s)
        # A `B` ends any current span and starts a new span
        if func == span_format.BEGIN:
            if span is not None:
                # There was a previously active span, This is an error, the span should have been closed by
                # either an `E` or and `S` before starting a new one.
                if i > 0:
                    prev_func = extract_function(seq[i - 1])
                    if prev_func not in (span_foramt.END, span_format.SINGLE):
                        LOGGER.warning("Illegal Label: `%s` ends span at %d", prev_func, i - 1)
                        errors.append(Error(i - 1, "Illegal End", safe_get(seq, i - 1), safe_get(seq, i - 2), s))
                spans.append(Span(span, start=tokens[0], end=tokens[-1] + 1, tokens=tuple(tokens)))
            span = _type
            tokens = [i]
            # Checking if this `B` causes errors.
            if i < len(seq) - 1:
                next_func = extract_function(seq[i + 1])
                # Look ahead to see if `B` token should actual be can `S` because it is only a single token
                # We only check for `B`, `S` and `O` because an illegal transition to an `I` or `E` will get
                # warned when we actually process that token
                if next_func in (span_format.BEGIN, span_format.SINGLE, TokenFunction.OUTSIDE):
                    LOGGER.warning("Illegal Label: Single `B` token span at %d", i)
                    errors.append(Error(i, "Illegal Single", s, safe_get(seq, i - 1), safe_get(seq, i + 1)))
            # A `B` as the last token is an error because it would result in a single span of a `B`
            elif i == len(seq) - 1:
                LOGGER.warning("Illegal Label: `B` as final token %d", i)
                errors.append(Error(i, "Illegal Final", s, safe_get(seq, i - 1), safe_get(seq, i + 1)))
        # A `S` ends any active span and creates a new single token span
        elif func == span_format.SINGLE:
            # There was a previously active span, This is an error, the span should have been closed by
            # either an `E` or and `S` before starting a new one.
            if span is not None:
                if i > 0:
                    prev_func = extract_function(seq[i - 1])
                    if prev_func not in (span_format.END, span_format.SINGLE):
                        LOGGER.warning("Illegal Label: `%s` ends span at %d", prev_func, i - 1)
                        errors.append(Error(i - 1, "Illegal End", safe_get(seq, i - 1), safe_get(seq, i - 2), s))
                # Flush this current span
                spans.append(Span(span, start=tokens[0], end=tokens[-1] + 1, tokens=tuple(tokens)))
            # Create a new span that covers this `S`
            spans.append(Span(_type, start=i, end=i + 1, tokens=(i,)))
            # Set the active span to None
            span = None
            tokens = []
        # An `I` will continue a span when the types match and start a new one otherwise.
        elif func == span_format.INSIDE:
            if span is not None:
                # Continue the entity
                if _type == span:
                    tokens.append(i)
                # Out types mismatch, save the current span and start a new one
                else:
                    LOGGER.warning("Illegal Label: `I` doesn't match previous token at %d", i)
                    errors.append(Error(i, "Illegal Transition", s, safe_get(seq, i - 1), safe_get(seq, i + 1)))
                    spans.append(Span(span, start=tokens[0], end=tokens[-1] + 1, tokens=tuple(tokens)))
                    span = _type
                    tokens = [i]
            # There was no previous entity we start one with this `I` but this is an error
            else:
                LOGGER.warning("Illegal Label: starting a span with `I` at %d", i)
                errors.append(Error(i, "Illegal Start", s, safe_get(seq, i - 1), safe_get(seq, i + 1)))
                span = _type
                tokens = [i]
            # Look ahead to see if this `I` is the last token. This will causes an illegal span because we
            # won't close the span so log this error.
            if i == len(seq) - 1:
                LOGGER.warning("Illegal Label: `I` as final token at %d", i)
                errors.append(Error(i, "Illegal Final", s, safe_get(seq, i - 1), safe_get(seq, i + 1)))
        # An `E` will close the currently active span if the type matches. Otherwise we close the current span,
        # create a new span, and immediately close it because we are an `E`
        elif func == span_format.END:
            if span is not None:
                # Type matches to close the span correctly
                if _type == span:
                    tokens.append(i)
                    spans.append(Span(span, start=tokens[0], end=tokens[-1] + 1, tokens=tuple(tokens)))
                    span = None
                    tokens = []
                # Type mismatch
                else:
                    # Log an error that the `E` doesn't match
                    LOGGER.warning("Illegal Label: `E` doesn't match previous token at %d", i)
                    errors.append(Error(i, "Illegal Transition", s, safe_get(seq, i - 1), safe_get(seq, i + 1)))
                    # Save out the active span
                    spans.append(Span(span, start=tokens[0], end=i, tokens=tuple(tokens)))
                    # Save out the new span this `E` opens and closes
                    spans.append(Span(_type, start=i, end=i + 1, tokens=(i,)))
                    # Set the active span to None
                    span = None
                    tokens = []
            # There was no span so start and end it with this `E`
            else:
                LOGGER.warning("Illegal Label: starting a span with `E` at %d", i)
                errors.append(Error(i, "Illegal Start", s, safe_get(seq, i - 1), safe_get(seq, i + 1)))
                spans.append(Span(_type, start=i, end=i + 1, tokens=(i,)))
                span = None
                tokens = []
        # An `O` cuts off the active entity
        else:
            # There was a previously active span, This is an error, the span should have been closed by
            # either an `E` or and `S` before having an O
            if span is not None:
                if i > 0:
                    prev_func = extract_function(seq[i - 1])
                    if prev_func not in (span_format.END, span_format.SINGLE):
                        LOGGER.warning("Illegal Label: `%s` ends span at %d", prev_func, i - 1)
                        errors.append(Error(i - 1, "Illegal End", safe_get(seq, i - 1), safe_get(seq, i - 2), s))
                spans.append(Span(span, start=tokens[0], end=tokens[-1] + 1, tokens=tuple(tokens)))
                span = None
                tokens = []
    if span is not None:
        # There was an active entity that fell off the end of the sequence. This should be an error because
        # it means that the span hasn't ended with an `E` or an `S` but we catch these errors by looking
        # ahead in the B or I section instead if doing it here.
        spans.append(Span(span, start=tokens[0], end=tokens[-1] + 1, tokens=tuple(tokens)))
        span = None
        tokens = []
    return spans, errors


def parse_spans_iobes(seq: List[str]) -> List[Span]:
    return parse_spans_iobes_with_errors(seq)[0]


def parse_spans_iobes_with_errors(seq: List[str]) -> Tuple[List[Span], List[Error]]:
    return parse_spans_with_end_with_errors(seq, IOBES)


def parse_spans_bilou(seq: List[str]) -> List[Span]:
    return parse_spans_with_end(seq, BILOU)


def parse_spans_bilou_with_errors(seq: List[str]) -> Tuple[List[Span], List[Error]]:
    return parse_spans_with_end_with_errors(seq, BILOU)


def parse_spans_bmeow(seq: List[str]) -> List[Span]:
    return parse_spans_with_end(seq, BMEOW)


parse_spans_bmewo = parse_spans_bmeow


def parse_spans_bmeow_with_errors(seq: List[str]) -> Tuple[List[Span], List[Error]]:
    return parse_spans_with_end_with_errors(seq, BMEOW)


parse_spans_bmewo_with_errors = parse_spans_bmeow_with_errors


def validate_labels(seq: List[str], span_type: SpanEncoding) -> bool:
    if span_type is SpanEncoding.IOB:
        return validate_labels_iob(seq)
    if span_type is SpanEncoding.BIO:
        return validate_labels_bio(seq)
    if span_type is SpanEncoding.IOBES:
        return validate_labels_iobes(seq)
    if span_type is SpanEncoding.BILOU:
        return validate_labels_bilou(seq)
    if span_type is SpanEncoding.BMEOW or span_type is SpanEncoding.BMEWO:
        return validate_labels_bmeow(seq)
    if span_type is SpanEncoding.TOKEN:
        return True
    raise ValueError(f"Unknown SpanEncoding Scheme, got: `{span_type}`")


def _validate_labels(parse: Callable[[List[str]], Tuple[List[Span], List[Error]]], seq: List[str]) -> bool:
    _, errors = parse(seq)
    return not errors


def validate_labels_iob(seq: List[str]) -> bool:
    return _validate_labels(parse_spans_iob_with_errors, seq)


def validate_labels_bio(seq: List[str]) -> bool:
    return _validate_labels(parse_spans_bio_with_errors, seq)


def validate_labels_iobes(seq: List[str]) -> bool:
    return _validate_labels(parse_spans_iobes_with_errors, seq)


def validate_labels_bilou(seq: List[str]) -> bool:
    return _validate_labels(parse_spans_bilou_with_errors, seq)


def validate_labels_bmeow(seq: List[str]) -> bool:
    return _validate_labels(parse_spans_bmeow_with_errors, seq)


def validate_labels_token(seq: List[str]) -> bool:
    return True


validate_labels_bmewo = validate_labels_bmeow
