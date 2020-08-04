__version__ = "1.4.1"

import logging
from enum import Enum
from typing import NamedTuple, Tuple


LOGGER = logging.getLogger("iobes")


class SpanFormat:
    """A description of a tag format.

    The anatomy of a tag is `{token-function}-{span-type}`. It has two parts, the second part
    is the type of the span. This is specific to the downstream task and can be things like
    `PER` or `LOC` for NER or things like `to_city` and `from_city` for slot filling used in a
    dialogue manager for air travel booking. The first part is the token function. It is generic
    across tasks and it is used when converting per-token labels into spans. Common examples is
    when a tag starts with a `B-` we know that it is the beginning of a new span or when a tag
    starts with `I-` we know that is is inside of a span.

    Note:
        Some tag formats have special `end` and `single` values for tags that end a span and
        tags that constitute a whole span in themselves while others don't. The span encoding
        formats that don't have end and single tokens just repeats of the `inside` and `begin`
        attributes respectively.
    """

    BEGIN = None  #: This is the token function that all tags that trigger a new span should have
    INSIDE = None  #: This is the token function that all tags inside of a span should have
    END = None  #: This is the token function that all tags at the end of a span should have
    SINGLE = None  #: This is the token function that all tags that constitute a span of length 1 should have

    def __init__(self):
        """These formats are designed to be singletons with class attributes so stop people from creating an object."""
        raise NotImplementedError("You cannot instantiate a SpanFormat object")


class TokenFunction:
    """Prefixes for tags that are used in decoding.

    In general tags can be broken into two parts, The first is the token function which
    tells you something about how the decoding parser should act when it hits this tag
    and the second half is the type (PER, LOC, etc) of the span.
    """

    OUTSIDE = "O"  #: This tag is not in any span, this is a rare one that is a whole tag, not just a prefix
    BEGIN = "B"  #: This tag starts a span
    INSIDE = "I"  #: This tag is in the middle of a span
    MIDDLE = "M"  #: This tag is in the middle of a span
    END = "E"  #: This tag ends a span
    LAST = "L"  #: This tag ends a span
    SINGLE = "S"  #: This tag by itself represents a span
    UNIT = "U"  #: This tag by itself represents a span
    WHOLE = "W"  #: This tag by itself represents a span
    GO = "<GO>"  #: This tag is a special tag for the beginning of a sequence
    EOS = "<EOS>"  #: This tag is a special tag for the end of a sequence


class IOB(SpanFormat):
    """The original IOB tagging format.

    ** TODO ** flesh out

    The first span encoding format proposed in `Ramshaw and Marcus, 1995`_

    This is the only format this is contextual, When two spans for the same type are touching then
    the first token of the second span would be a `B` where as in cases when the first token is
    not following (touching) another span of the same type it would be an `I`. So the value of the
    BEGIN tag isn't known without context.

    The same applies to the SINGLE tag.

    .. _Ramshaw and Marcus, 1995: https://www.aclweb.org/anthology/W95-0107/
    """

    BEGIN = None
    INSIDE = TokenFunction.INSIDE
    END = TokenFunction.INSIDE
    SINGLE = None


class BIO(SpanFormat):
    """The improved BIO tagging format.

    ** TODO ** flesh out

    This is a context independent format where all of the values are known beforehand. There is not
    special end tag though. An entity ends when there is an `O` or a different entity starts.
    """

    BEGIN = TokenFunction.BEGIN
    INSIDE = TokenFunction.INSIDE
    END = TokenFunction.INSIDE
    SINGLE = TokenFunction.BEGIN


class IOBES(SpanFormat):
    """The best tagging format.

    ** TODO ** flesh out

    This format adds an END tag that needs to show up at the end of entities. This format has been shown
    to be better than IOB or BIO (`Ratinov and Roth, 2009`_) and should be used instead.

    .. _Ratinov and Roth, 2009: https://www.aclweb.org/anthology/W09-1119/
    """

    BEGIN = TokenFunction.BEGIN
    INSIDE = TokenFunction.INSIDE
    END = TokenFunction.END
    SINGLE = TokenFunction.SINGLE


class BILOU(SpanFormat):
    """The BILOU format.

    ** TODO ** flesh out

    This is the same as the IOBES format but we just have different values for the END and SINGLE tokens.
    """

    BEGIN = TokenFunction.BEGIN
    INSIDE = TokenFunction.INSIDE
    END = TokenFunction.LAST
    SINGLE = TokenFunction.UNIT


class BMEOW(SpanFormat):
    """The BMEOW format.

    ** TODO ** flesh out

    From `Borthwick, 1999`_

    This is the same as the IOBES format but we just have different values for the INSIDE and SINGLE tokens.

    .. _Borthwick, 1999: https://www.math.nyu.edu/media/mathfin/publications/borthwick_andrew.pdf
    """

    BEGIN = TokenFunction.BEGIN
    INSIDE = TokenFunction.MIDDLE
    END = TokenFunction.END
    SINGLE = TokenFunction.WHOLE


BMEWO = (  #: This is the same as BMEOW and what a lot of people actually call it but having `meow` in it seems better lol.
    BMEOW
)


class TOKEN(SpanFormat):
    """A format to use when processing tokens.

    ** TODO ** flesh out

    In this case the tags are supposed to be for the tokens themselves instead of being converted into spans. This is
    for things like Part of Speech tagging and the like.
    """


class SpanEncoding(Enum):
    """An enumeration of the kind of span encoding schemes we support processing."""

    TOKEN = TOKEN
    IOB = IOB
    BIO = BIO
    IOBES = IOBES
    BILOU = BILOU
    BMEOW = BMEOW
    BMEWO = BMEWO

    @classmethod
    def from_string(cls, value) -> "SpanEncoding":
        """Parse string into a specific span encoding format.

        Args:
            value: The string to dispatch to encoding on.

        Raises:
            ValueError: If the string cannot be recognized as pointing to a specific SpanEncoding format.

        Returns:
            The SpanEncoding member.
        """
        value = value.lower().strip()
        if value == "iob":
            return cls.IOB
        if value in ("iob2", "bio"):
            return cls.BIO
        if value == "iobes":
            return cls.IOBES
        if value in ("bilou", "bioul"):
            return cls.BILOU
        if value in ("bmewo", "bmeow"):
            return cls.BMEOW
        if value == "token":
            return cls.TOKEN
        raise ValueError(f"Unknown Encoding scheme, got: `{value}`")


class Span(NamedTuple):
    """Our representation of a span of text.

    Note:
        Our `end` attribute of a span is one greater than the index of the final token
        in the span. This is so that python list slicing works. For example,
        `tokens[span.start : span.end]` will yield the surface form of the span.

    Args:
        type: The type of the span in our downstream task, things like `PER` or `LOC`.
        start: The index into the tokens list where the span starts.
        end: The index of the last token of the span plus 1.
        tokens: The indices that are part of the span.
    """

    type: str
    start: int
    end: int
    tokens: Tuple[int]


class ErrorType(Enum):
    pass


class Error(NamedTuple):
    """An error encountered when parsing tags into spans.

    Args:
        location: The index where the error occurred
        type: What kind of error is it. **TODO** These types need to be enumerated and hammer out the specifics
        current: The tag at the index of the error
        previous: The previous tag
        next: The next tag
    """

    location: int
    type: str
    current: str
    previous: str
    next: str

    def __str__(self):
        return f"{self.type} error at index {self.location}."


from iobes.convert import (
    iob_to_bio,
    iob_to_iobes,
    iob_to_bilou,
    iob_to_bmeow,
    iob_to_bmewo,
    bio_to_iob,
    bio_to_iobes,
    bio_to_bilou,
    bio_to_bmeow,
    bio_to_bmewo,
    iobes_to_iob,
    iobes_to_bio,
    iobes_to_bilou,
    iobes_to_bmeow,
    iobes_to_bmewo,
    bilou_to_iob,
    bilou_to_bio,
    bilou_to_iobes,
    bilou_to_bmeow,
    bilou_to_bmewo,
    bmeow_to_iob,
    bmeow_to_bio,
    bmeow_to_iobes,
    bmeow_to_bilou,
    bmewo_to_iob,
    bmewo_to_bio,
    bmewo_to_iobes,
    bmewo_to_bilou,
)
from iobes.parse import (
    parse_spans,
    parse_spans_token,
    parse_spans_iob,
    parse_spans_bio,
    parse_spans_iobes,
    parse_spans_bilou,
    parse_spans_bmeow,
    parse_spans_bmewo,
    parse_spans_with_errors,
    parse_spans_token_with_errors,
    parse_spans_iob_with_errors,
    parse_spans_bio_with_errors,
    parse_spans_iobes_with_errors,
    parse_spans_bilou_with_errors,
    parse_spans_bmeow_with_errors,
    parse_spans_bmewo_with_errors,
    validate_labels,
    validate_labels_iob,
    validate_labels_bio,
    validate_labels_iobes,
    validate_labels_bilou,
    validate_labels_bmeow,
    validate_labels_bmewo,
)
from iobes.transition import (
    Transition,
    transitions_legality,
    iob_transitions_legality,
    bio_transitions_legality,
    iobes_transitions_legality,
    bilou_transitions_legality,
    bmeow_transitions_legality,
    bmewo_transitions_legality,
    transitions_to_tuple_map,
    transitions_to_map,
)
from iobes.write import (
    write_tags,
    write_iob_tags,
    write_bio_tags,
    write_iobes_tags,
    write_bilou_tags,
    write_bmeow_tags,
    write_bmewo_tags,
)
from iobes.utils import (
    extract_type,
    extract_function,
)
