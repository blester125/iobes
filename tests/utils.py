import string
import random
from typing import Optional, List
from iobes import Span
from iobes.utils import extract_type


def random_string(length: int = None, min_length: int = 3, max_length: int = 6):
    length = random.randint(min_length, max_length) if length is None else length
    return "".join(random.choice(string.ascii_letters) for _ in range(length))


def generate_spans(
    types: Optional[List[str]] = None,
    max_spans: int = 5,
    min_spans: int = 0,
    max_span_len: int = 4,
    min_span_len: int = 1,
    min_space: int = 0,
    max_space: int = 3,
) -> List[Span]:
    types = ["A", "B", "C", "AA"] if types is None else types
    n_spans = random.randint(min_spans, max_spans)
    spans = []
    i = 0
    for _ in range(n_spans):
        ty = random.choice(types)
        length = random.randint(min_span_len, max_span_len)
        gap = random.randint(min_space, max_space)
        start = i + gap
        end = start + length
        i = end
        spans.append(Span(ty, start, end, tuple(range(start, end))))
    end = random.randint(min_space, max_space)
    return spans, i + end


def generate_iobes(spans, length):
    tags = ["O"] * length
    for span in spans:
        if len(span.tokens) == 1:
            tags[span.tokens[0]] = f"S-{span.type}"
            continue
        tags[span.tokens[0]] = f"B-{span.type}"
        tags[span.tokens[-1]] = f"E-{span.type}"
        for i in span.tokens[1:-1]:
            tags[i] = f"I-{span.type}"
    return tags


def generate_bilou(spans, length):
    tags = ["O"] * length
    for span in spans:
        if len(span.tokens) == 1:
            tags[span.tokens[0]] = f"U-{span.type}"
            continue
        tags[span.tokens[0]] = f"B-{span.type}"
        tags[span.tokens[-1]] = f"L-{span.type}"
        for i in span.tokens[1:-1]:
            tags[i] = f"I-{span.type}"
    return tags


def generate_bmeow(spans, length):
    tags = ["O"] * length
    for span in spans:
        if len(span.tokens) == 1:
            tags[span.tokens[0]] = f"W-{span.type}"
            continue
        tags[span.tokens[0]] = f"B-{span.type}"
        tags[span.tokens[-1]] = f"E-{span.type}"
        for i in span.tokens[1:-1]:
            tags[i] = f"M-{span.type}"
    return tags


def generate_bio(spans, length):
    tags = ["O"] * length
    for span in spans:
        tags[span.tokens[0]] = f"B-{span.type}"
        for i in span.tokens[1:]:
            tags[i] = f"I-{span.type}"
    return tags


def generate_iob(spans, length):
    tags = ["O"] * length
    for span in spans:
        for i in span.tokens:
            tags[i] = f"I-{span.type}"
    for span in spans:
        if span.tokens[0] != 0 and extract_type(tags[span.tokens[0] - 1]) == span.type:
            tags[span.tokens[0]] = f"B-{span.type}"
    return tags
