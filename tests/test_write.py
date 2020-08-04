#!/usr/bin/env python3


import random
import string
from copy import deepcopy
from typing import Optional
import pytest
from iobes import Span, SpanEncoding
from iobes.write import (
    sort_spans,
    write_tags,
    make_tag,
)


def random_string(length: Optional[int] = None, min_: int = 3, max_: int = 5) -> str:
    length = length if length is not None else random.randint(min_, max_)
    return "".join([random.choice(string.ascii_letters) for _ in range(length)])


@pytest.fixture
def generate_spans():
    span_count = random.randint(1, 6)
    span_length_min = 1
    span_length_max = 4
    span_gap_min = 0
    span_gap_max = 3
    spans = []
    i = 0
    for _ in range(span_count):
        span_start = i + random.randint(span_gap_min, span_gap_max)
        span_length = random.randint(span_length_min, span_length_max)
        span_end = span_start + span_length
        span_type = random_string()
        spans.append(Span(span_type, span_start, span_end, tokens=list(range(span_start, span_end))))
        i = span_end
    return spans


def test_sort_spans(generate_spans):
    gold_spans = deepcopy(generate_spans)
    random.shuffle(generate_spans)
    assert sort_spans(generate_spans) == gold_spans


def test_make_tag():
    func = random_string()
    type = random_string()
    delim = random_string()
    gold = func + delim + type
    assert make_tag(func, type, delim) == gold
