__version__ = "0.0.0"

import logging
from enum import Enum
from typing import NamedTuple, List


LOGGER = logging.getLogger("iobes")


class Function:
    OUTSIDE = "O"
    BEGIN = "B"
    INSIDE = "I"
    MIDDLE = "M"
    END = "E"
    LAST = "L"
    SINGLE = "S"
    UNIT = "U"
    WHOLE = "W"


class Encoding(Enum):
    IOB = 1
    BIO = 2
    IOBES = 3
    BILOU = 4
    BMEWO = 5
    TOKEN = 6

    @classmethod
    def from_string(cls, value):
        value = value.lower().strip()
        if value == "iob":
            return cls.IOB
        if value in ("iob2", "bio"):
            return cls.BIO
        if value == "iobes":
            return cls.IOBES
        if value == "bilou":
            return cls.BILOU
        if value == "bmewo":
            return cls.BMEWO
        if value == "token":
            return cls.TOKEN
        raise ValueError(f"Unknown Encoding Scheme, got: `{value}`")


class Span(NamedTuple):
    type: str
    start: int
    end: int
    tokens: List[int]


class Error(NamedTuple):
    location: int
    type: str