from typing import List, Tuple, Callable
from iobes import Span, SpanEncoding, SpanFormat, Error, TokenFunction, LOGGER, IOB, BIO, IOBES, BILOU, BMEOW
from iobes.utils import extract_function, extract_type, safe_get, sort_spans, sort_errors


def parse_spans(seq: List[str], span_type: SpanEncoding) -> List[Span]:
    """Parse a sequence of labels into a list of spans.

    Note:
        In the case where labels violate the span encoded scheme, for example the
        tag is a new type (like ``I-ORG``) in the middle of a span of another type
        (like ``PER``) without a proper starting token (``B-ORG``) we will finish
        the initial span and start a new one, resulting in two spans. This follows
        the ``conlleval.pl`` script.

    Note:
        Span are returned sorted by their starting location. Due to the fact that
        spans are not allowed to overlap there is no resolution policy when two
        spans have same starting location.

    Args:
        seq: The sequence of labels.
        span_type: The span encoding format used to encode the spans into the labels.

    Returns:
        A list of spans.
    """
    return parse_spans_with_errors(seq, span_type)[0]


def parse_spans_with_errors(seq: List[str], span_type: SpanEncoding) -> Tuple[List[Span], List[Error]]:
    """Parse a sequence of labels into a list of spans but return any violations of the encoding scheme.

    Note:
        In the case where labels violate the span encoded scheme, for example the
        tag is a new type (like ``I-ORG``) in the middle of a span of another type
        (like ``PER``) without a proper starting token (``B-ORG``) we will finish
        the initial span and start a new one, resulting in two spans. This follows
        the ``conlleval.pl`` script.

    Note:
        Span are returned sorted by their starting location. Due to the fact that
        spans are not allowed to overlap there is no resolution policy when two
        spans have same starting location.

    Note:
        Errors are returned sorted by the location where the violation occurred. In the
        case a single transition triggered multiple errors they are sorted lexically based
        on the error type.

    Args:
        seq: The sequence of labels
        span_type: The span encoding format the spans are encoded into the labels with

    Returns:
        A list of spans and a list of errors.
    """
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
    """Parse a sequence of labels into a list of spans.

    Note:
        Span are returned sorted by their starting location. Due to the fact that
        spans are not allowed to overlap there is no resolution policy when two
        spans have same starting location.

    Args:
        seq: The sequence of labels.

    Returns:
        A list of spans.
    """
    return parse_spans_token_with_errors(seq)[0]


def parse_spans_token_with_errors(seq: List[str]) -> Tuple[List[Span], List[Error]]:
    """Parse a sequence of labels into a list of spans but return any violations of the encoding scheme.

    Note:
        Span are returned sorted by their starting location. Due to the fact that
        spans are not allowed to overlap there is no resolution policy when two
        spans have same starting location.

    Note:
        Errors are returned sorted by the location where the violation occurred. In the
        case a single transition triggered multiple errors they are sorted lexically based
        on the error type.

    Args:
        seq: The sequence of labels

    Returns:
        A list of spans and a list of errors.
    """
    return [Span(type=t, start=i, end=i + 1, tokens=(i,)) for i, t in enumerate(seq)], []


def parse_spans_iob(seq: List[str]) -> List[Span]:
    """Parse a sequence of IOB encoded labels into a list of spans.

    Note:
        Span are returned sorted by their starting location. Due to the fact that
        spans are not allowed to overlap there is no resolution policy when two
        spans have same starting location.

    Args:
        seq: The sequence of labels.

    Returns:
        A list of spans.
    """
    return parse_spans_iob_with_errors(seq)[0]


def parse_spans_iob_with_errors(seq: List[str]) -> Tuple[List[Span], List[Error]]:
    """Parse a sequence of IOB encoded labels into a list of spans but return any violations of the encoding scheme.

    Note:
        Span are returned sorted by their starting location. Due to the fact that
        spans are not allowed to overlap there is no resolution policy when two
        spans have same starting location.

    Note:
        Errors are returned sorted by the location where the violation occurred. In the
        case a single transition triggered multiple errors they are sorted lexically based
        on the error type.

    Args:
        seq: The sequence of labels

    Returns:
        A list of spans and a list of errors.
    """
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
    return sort_spans(spans), sort_errors(errors)


def parse_spans_bio(seq: List[str]) -> List[Span]:
    """Parse a sequence of BIO labels into a list of spans.

    Note:
        In the case where labels violate the span encoded scheme, for example the
        tag is a new type (like ``I-ORG``) in the middle of a span of another type
        (like ``PER``) without a proper starting token (``B-ORG``) we will finish
        the initial span and start a new one, resulting in two spans. This follows
        the ``conlleval.pl`` script.

    Note:
        Span are returned sorted by their starting location. Due to the fact that
        spans are not allowed to overlap there is no resolution policy when two
        spans have same starting location.

    Args:
        seq: The sequence of labels.

    Returns:
        A list of spans.
    """
    return parse_spans_bio_with_errors(seq)[0]


def parse_spans_bio_with_errors(seq: List[str]) -> Tuple[List[Span], List[Error]]:
    """Parse a sequence of BIO labels into a list of spans but return any violations of the encoding scheme.

    Note:
        In the case where labels violate the span encoded scheme, for example the
        tag is a new type (like ``I-ORG``) in the middle of a span of another type
        (like ``PER``) without a proper starting token (``B-ORG``) we will finish
        the initial span and start a new one, resulting in two spans. This follows
        the ``conlleval.pl`` script.

    Note:
        Span are returned sorted by their starting location. Due to the fact that
        spans are not allowed to overlap there is no resolution policy when two
        spans have same starting location.

    Note:
        Errors are returned sorted by the location where the violation occurred. In the
        case a single transition triggered multiple errors they are sorted lexically based
        on the error type.

    Args:
        seq: The sequence of labels

    Returns:
        A list of spans and a list of errors.
    """
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
    return sort_spans(spans), sort_errors(errors)


def parse_spans_with_end(seq: List[str], span_format: SpanFormat) -> List[Span]:
    """Parse a sequence of labels into a list of spans.

    Note:
        In the case where labels violate the span encoded scheme, for example the
        tag is a new type (like ``I-ORG``) in the middle of a span of another type
        (like ``PER``) without a proper starting token (``B-ORG``) we will finish
        the initial span and start a new one, resulting in two spans. This follows
        the ``conlleval.pl`` script.

    Note:
        Span are returned sorted by their starting location. Due to the fact that
        spans are not allowed to overlap there is no resolution policy when two
        spans have same starting location.

    Note:
        This is a generic function that can parse IOBES, BILOU, and BMEWO formats.

    Args:
        seq: The sequence of labels.
        span_format: A description of the span encoding format.

    Returns:
        A list of spans.
    """
    return parse_spans_with_end_with_errors(seq, span_format)[0]


def parse_spans_with_end_with_errors(seq: List[str], span_format: SpanFormat) -> Tuple[List[Span], List[Error]]:
    """Parse a sequence of labels into a list of spans but return any violations of the encoding scheme.

    Note:
        In the case where labels violate the span encoded scheme, for example the
        tag is a new type (like ``I-ORG``) in the middle of a span of another type
        (like ``PER``) without a proper starting token (``B-ORG``) we will finish
        the initial span and start a new one, resulting in two spans. This follows
        the ``conlleval.pl`` script.

    Note:
        Span are returned sorted by their starting location. Due to the fact that
        spans are not allowed to overlap there is no resolution policy when two
        spans have same starting location.

    Note:
        Errors are returned sorted by the location where the violation occurred. In the
        case a single transition triggered multiple errors they are sorted lexically based
        on the error type.

    Note:
        This is a generic function that can parse IOBES, BILOU, and BMEWO formats.

    Args:
        seq: The sequence of labels

    Returns:
        A list of spans and a list of errors.
    """
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
                    if prev_func not in (span_format.END, span_format.SINGLE):
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
    return sort_spans(spans), sort_errors(errors)


def parse_spans_iobes(seq: List[str]) -> List[Span]:
    """Parse a sequence of IOBES encoded labels into a list of spans.

    Note:
        In the case where labels violate the span encoded scheme, for example the
        tag is a new type (like ``I-ORG``) in the middle of a span of another type
        (like ``PER``) without a proper starting token (``B-ORG``) we will finish
        the initial span and start a new one, resulting in two spans. This follows
        the ``conlleval.pl`` script.

    Note:
        Span are returned sorted by their starting location. Due to the fact that
        spans are not allowed to overlap there is no resolution policy when two
        spans have same starting location.

    Args:
        seq: The sequence of labels.

    Returns:
        A list of spans.
    """
    return parse_spans_iobes_with_errors(seq)[0]


def parse_spans_iobes_with_errors(seq: List[str]) -> Tuple[List[Span], List[Error]]:
    """Parse a sequence of IOBES encoded labels into a list of spans but return any violations of the encoding scheme.

    Note:
        In the case where labels violate the span encoded scheme, for example the
        tag is a new type (like ``I-ORG``) in the middle of a span of another type
        (like ``PER``) without a proper starting token (``B-ORG``) we will finish
        the initial span and start a new one, resulting in two spans. This follows
        the ``conlleval.pl`` script.

    Note:
        Span are returned sorted by their starting location. Due to the fact that
        spans are not allowed to overlap there is no resolution policy when two
        spans have same starting location.

    Note:
        Errors are returned sorted by the location where the violation occurred. In the
        case a single transition triggered multiple errors they are sorted lexically based
        on the error type.

    Args:
        seq: The sequence of labels

    Returns:
        A list of spans and a list of errors.
    """
    return parse_spans_with_end_with_errors(seq, IOBES)


def parse_spans_bilou(seq: List[str]) -> List[Span]:
    """Parse a sequence of BILOU labels into a list of spans.

    Note:
        In the case where labels violate the span encoded scheme, for example the
        tag is a new type (like ``I-ORG``) in the middle of a span of another type
        (like ``PER``) without a proper starting token (``B-ORG``) we will finish
        the initial span and start a new one, resulting in two spans. This follows
        the ``conlleval.pl`` script.

    Note:
        Span are returned sorted by their starting location. Due to the fact that
        spans are not allowed to overlap there is no resolution policy when two
        spans have same starting location.

    Args:
        seq: The sequence of labels.

    Returns:
        A list of spans.
    """
    return parse_spans_with_end(seq, BILOU)


def parse_spans_bilou_with_errors(seq: List[str]) -> Tuple[List[Span], List[Error]]:
    """Parse a sequence of BILOU labels into a list of spans but return any violations of the encoding scheme.

    Note:
        In the case where labels violate the span encoded scheme, for example the
        tag is a new type (like ``I-ORG``) in the middle of a span of another type
        (like ``PER``) without a proper starting token (``B-ORG``) we will finish
        the initial span and start a new one, resulting in two spans. This follows
        the ``conlleval.pl`` script.

    Note:
        Span are returned sorted by their starting location. Due to the fact that
        spans are not allowed to overlap there is no resolution policy when two
        spans have same starting location.

    Note:
        Errors are returned sorted by the location where the violation occurred. In the
        case a single transition triggered multiple errors they are sorted lexically based
        on the error type.

    Args:
        seq: The sequence of labels

    Returns:
        A list of spans and a list of errors.
    """
    return parse_spans_with_end_with_errors(seq, BILOU)


def parse_spans_bmeow(seq: List[str]) -> List[Span]:
    """Parse a sequence of BMEOW labels into a list of spans.

    Note:
        In the case where labels violate the span encoded scheme, for example the
        tag is a new type (like ``I-ORG``) in the middle of a span of another type
        (like ``PER``) without a proper starting token (``B-ORG``) we will finish
        the initial span and start a new one, resulting in two spans. This follows
        the ``conlleval.pl`` script.

    Note:
        Span are returned sorted by their starting location. Due to the fact that
        spans are not allowed to overlap there is no resolution policy when two
        spans have same starting location.

    Args:
        seq: The sequence of labels.

    Returns:
        A list of spans.
    """
    return parse_spans_with_end(seq, BMEOW)


def parse_spans_bmewo(seq: List[str]) -> List[Span]:
    """Parse a sequence of BMEWO labels into a list of spans.

    Note:
        Alias for :py:func:`~iobes.parse.parse_spans_bmeow`

    Note:
        In the case where labels violate the span encoded scheme, for example the
        tag is a new type (like ``I-ORG``) in the middle of a span of another type
        (like ``PER``) without a proper starting token (``B-ORG``) we will finish
        the initial span and start a new one, resulting in two spans. This follows
        the ``conlleval.pl`` script.

    Note:
        Span are returned sorted by their starting location. Due to the fact that
        spans are not allowed to overlap there is no resolution policy when two
        spans have same starting location.

    Args:
        seq: The sequence of labels.

    Returns:
        A list of spans.
    """
    return prase_spans_bmeow(seq)


def parse_spans_bmeow_with_errors(seq: List[str]) -> Tuple[List[Span], List[Error]]:
    """Parse a sequence of BMEOW labels into a list of spans but return any violations of the encoding scheme.

    Note:
        In the case where labels violate the span encoded scheme, for example the
        tag is a new type (like ``I-ORG``) in the middle of a span of another type
        (like ``PER``) without a proper starting token (``B-ORG``) we will finish
        the initial span and start a new one, resulting in two spans. This follows
        the ``conlleval.pl`` script.

    Note:
        Span are returned sorted by their starting location. Due to the fact that
        spans are not allowed to overlap there is no resolution policy when two
        spans have same starting location.

    Note:
        Errors are returned sorted by the location where the violation occurred. In the
        case a single transition triggered multiple errors they are sorted lexically based
        on the error type.

    Args:
        seq: The sequence of labels

    Returns:
        A list of spans and a list of errors.
    """
    return parse_spans_with_end_with_errors(seq, BMEOW)


def parse_spans_bmewo_with_errors(seq: List[str]) -> Tuple[List[Span], List[Error]]:
    """Parse a sequence of BMEOW labels into a list of spans but return any violations of the encoding scheme.

    Note:
        Alias for :py:func:`~iobes.parse.parse_spans_bmeow_with_errors`

    Note:
        In the case where labels violate the span encoded scheme, for example the
        tag is a new type (like ``I-ORG``) in the middle of a span of another type
        (like ``PER``) without a proper starting token (``B-ORG``) we will finish
        the initial span and start a new one, resulting in two spans. This follows
        the ``conlleval.pl`` script.

    Note:
        Span are returned sorted by their starting location. Due to the fact that
        spans are not allowed to overlap there is no resolution policy when two
        spans have same starting location.

    Note:
        Errors are returned sorted by the location where the violation occurred. In the
        case a single transition triggered multiple errors they are sorted lexically based
        on the error type.

    Args:
        seq: The sequence of labels

    Returns:
        A list of spans and a list of errors.
    """
    return parse_spans_bmeow_with_errors


def validate_tags(tags: List[str], span_type: SpanEncoding) -> bool:
    """Check for errors in a tag scheme.

    Args:
        tags: The tags we are parsing.
        span_type: The span encoding scheme we have used.

    Raises:
        ValueError: If the span encoding scheme isn't recognized.

    Returns:
        True if the tags don't have any formatting errors, False otherwise.
    """
    if span_type is SpanEncoding.IOB:
        return validate_tags_iob(tags)
    if span_type is SpanEncoding.BIO:
        return validate_tags_bio(tags)
    if span_type is SpanEncoding.IOBES:
        return validate_tags_iobes(tags)
    if span_type is SpanEncoding.BILOU:
        return validate_tags_bilou(tags)
    if span_type is SpanEncoding.BMEOW or span_type is SpanEncoding.BMEWO:
        return validate_tags_bmeow(tags)
    if span_type is SpanEncoding.TOKEN:
        return validate_tags_token(tags)
    raise ValueError(f"Unknown SpanEncoding Scheme, got: `{span_type}`")


def _validate_tags(parse: Callable[[List[str]], Tuple[List[Span], List[Error]]], tags: List[str]) -> bool:
    """Check for errors in a tag scheme.

    Args:
        parse: A function that parses spans and return spans and errors.
        tags: The tags we are parsing.

    Returns:
        True if the tags don't have any formatting errors, False otherwise.
    """
    _, errors = parse(tags)
    return not errors


def validate_tags_iob(tags: List[str]) -> bool:
    """Check for errors in IOB tags.

    Args:
        tags: The IOB tags we are parsing.

    Returns:
        True if the IOB tags are well-formed, False otherwise.
    """
    return _validate_tags(parse_spans_iob_with_errors, tags)


def validate_tags_bio(tags: List[str]) -> bool:
    """Check for errors in BIO tags.

    Args:
        tags: The BIO tags we are parsing.

    Returns:
        True if the BIO tags are well-formed, False otherwise.
    """
    return _validate_tags(parse_spans_bio_with_errors, tags)


def validate_tags_iobes(tags: List[str]) -> bool:
    """Check for errors in IOBES tags.

    Args:
        tags: The IOBES tags we are parsing.

    Returns:
        True if the IOBES tags are well-formed, False otherwise.
    """
    return _validate_tags(parse_spans_iobes_with_errors, tags)


def validate_tags_bilou(tags: List[str]) -> bool:
    """Check for errors in BILOU tags.

    Args:
        tags: The BILOU tags we are parsing.

    Returns:
        True if the BILOU tags are well-formed, False otherwise.
    """
    return _validate_tags(parse_spans_bilou_with_errors, tags)


def validate_tags_bmeow(tags: List[str]) -> bool:
    """Check for errors in BMEOW tags.

    Args:
        tags: The BMEOW tags we are parsing.

    Returns:
        True if the BMEOW tags are well-formed, False otherwise.
    """
    return _validate_tags(parse_spans_bmeow_with_errors, tags)


def validate_tags_token(tags: List[str]) -> bool:
    """Check for errors in TOKEN tags.

    Note:
        Token tags are not processed into spans so all sequences are valid.

    Args:
        tags: The TOKEN tags we are parsing.

    Returns:
        True
    """
    return True


def validate_tags_bmewo(tags: List[str]) -> bool:
    """Check for errors in BMEWO tags.

    Note:
        Alias for :py:func:`~iobes.parse.validate_labels_bmeow`

    Args:
        tags: The BMEWO tags we are parsing.

    Returns:
        True if the BMEWO tags are well-formed, False otherwise.
    """
    return validate_tags_bmeow(tags)
