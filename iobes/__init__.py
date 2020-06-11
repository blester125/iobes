__version__ = "1.2.1"

import logging
from enum import Enum
from typing import NamedTuple, List


LOGGER = logging.getLogger("iobes")


class TokenFunction:
    """Prefixes for tags that are used in decoding.

    In general tags can be broken into two parts, The first is the token function which
    tells you something about how the decoding parser should act when it hits this tag
    and the second half is the type (PER, LOC, etc) of the span.
    """

    OUTSIDE = "O"  # This tag is not in any span, this is a rare one that is a whole tag, not just a prefix
    BEGIN = "B"  # This tag starts a span
    INSIDE = "I"  # This tag is in the middle of a span
    MIDDLE = "M"  # This tag is in the middle of a span
    END = "E"  # This tag ends a span
    LAST = "L"  # This tag ends a span
    SINGLE = "S"  # This tag by itself represents a span
    UNIT = "U"  # This tag by itself represents a span
    WHOLE = "W"  # This tag by itself represents a span
    GO = "<GO>"  # This tag is a special tag for the beginning of a sequence
    EOS = "<EOS>"  # This tag is a special tag for the end of a sequence


class SpanFormat:
    """A description of a tag format.

    BEGIN, INSIDE, and END are the TokenFunction values that start, are in the middle, and
    end a span. SINGLE is the TokenFunction value when a single tag is a span
    """

    BEGIN = None
    INSIDE = None
    END = None
    SINGLE = None

    def __init__(self):
        """These are all based on class attributes so stop people from creating a specific object."""
        raise NotImplementedError("You cannot instantiate a SpanFormat object")


class IOB(SpanFormat):
    """The original IOB tagging format.

    This is the only format this is contextual, When two spans for the same type are touching then
    the first token of the second span would be a `B` where as in cases when the first token is
    not following (touching) another span of the same type it would be an `I`. So the value of the
    BEGIN tag isn't known without context.

    The same applies to the SINGLE tag.
    """

    BEGIN = None
    INSIDE = TokenFunction.INSIDE
    END = TokenFunction.INSIDE
    SINGLE = None


class BIO(SpanFormat):
    """The improved BIO tagging format.

    This is a context independent format where all of the values are known beforehand. There is not
    special end tag though. An entity ends when there is an `O` or a different entity starts.
    """

    BEGIN = TokenFunction.BEGIN
    INSIDE = TokenFunction.INSIDE
    END = TokenFunction.INSIDE
    SINGLE = TokenFunction.BEGIN


class IOBES(SpanFormat):
    """The best tagging format.

    This format adds an END tag that needs to show up at the end of entities. This format has been shown
    to be better than IOB or BIO (Ratinov and Roth, 2009) and should be used instead.
    """

    BEGIN = TokenFunction.BEGIN
    INSIDE = TokenFunction.INSIDE
    END = TokenFunction.END
    SINGLE = TokenFunction.SINGLE


class BILOU(SpanFormat):
    """The BILOU format.

    This is the same as the IOBES format but we just have different values for the END and SINGLE tokens.
    """

    BEGIN = TokenFunction.BEGIN
    INSIDE = TokenFunction.INSIDE
    END = TokenFunction.LAST
    SINGLE = TokenFunction.UNIT


class BMEOW(SpanFormat):
    """The BMEOW format.

    This is the same as the IOBES format but we just have different values for the INSIDE and SINGLE tokens.
    """

    BEGIN = TokenFunction.BEGIN
    INSIDE = TokenFunction.MIDDLE
    END = TokenFunction.END
    SINGLE = TokenFunction.WHOLE


BMEWO = (
    BMEOW  # This is the same as BMEOW and what a lot of people actually call it but have `meow` in it seems better lol.
)


class TOKEN(SpanFormat):
    """A format to use when processing tokens.

    In this case the tags are supposed to be for the tokens themselves instead of being converted into spans. This is
    for things like Part of Speech tagging and the like.
    """

    pass


class SpanEncoding(Enum):
    IOB = IOB
    BIO = BIO
    IOBES = IOBES
    BILOU = BILOU
    BMEOW = BMEOW
    BMEWO = BMEWO
    TOKEN = TOKEN

    @classmethod
    def from_string(cls, value):
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
    """Our representation of a span of text

    type is the type of the span in our downstream task, things like PER or LOC
    start is the index of where the span starts
    end is the index after the span ends. This is so that normal python slicing works
        tokens[span.start:span.end] gives you the surface of the span
    tokens is a list of indices what are part of the span
    """

    type: str
    start: int
    end: int
    tokens: List[int]


class Error(NamedTuple):
    """An error encountered when parsing tags.

    location is the index that the error happened at
    type is the kind of error is it
    current is the tag at the error index
    previous is the last tag (probably part of the error)
    next is the next tag (probably part of the error)
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
from iobes.utils import (
    extract_type,
    extract_function,
)
