__version__ = "1.2.1"

import logging
from enum import Enum
from typing import NamedTuple, List


LOGGER = logging.getLogger("iobes")

"""
I though about have specific classes for each of the span encoding types like so

class IOBES:
    START = "B"
    INSIDE = "I"
    END = "E"
    SINGLE = "S"

The problem is handling the IOB format where the first token is different depending on the context
so it didn't seem like a great solution.

These classes would also let us use the same parsing functions for IOBES, BILOU, and BMEOW/BMEWO but
given how easy this is covered with the conversion to IOBES it doesn't seem like it buys us a lot. Also
we would still need special code for the BIO stuff.
"""


class TokenFunction:
    OUTSIDE = "O"
    BEGIN = "B"
    INSIDE = "I"
    MIDDLE = "M"
    END = "E"
    LAST = "L"
    SINGLE = "S"
    UNIT = "U"
    WHOLE = "W"
    GO = "<GO>"
    EOS = "<EOS>"


class SpanEncoding(Enum):
    IOB = 1
    BIO = 2
    IOBES = 3
    BILOU = 4
    BMEOW = 5
    BMEWO = 6
    TOKEN = 7

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
    type: str
    start: int
    end: int
    tokens: List[int]


class Error(NamedTuple):
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
