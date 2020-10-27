import random
from copy import deepcopy
from iobes import Span, Error
from iobes.utils import safe_get, extract_function, extract_type, sort_spans, sort_errors
from utils import random_string


def test_extract_type():
    func, _type = random_string(), random_string()
    sep = random.choice(list("-~|!."))
    tag = sep.join([func, _type])
    assert extract_type(tag, sep) == _type


def test_extract_function():
    func, _type = random_string(), random_string()
    sep = random.choice(list("-~|!."))
    tag = sep.join([func, _type])
    assert extract_function(tag, sep) == func


def test_replace_safe_get():
    seq = [random_string() for _ in range(random.randint(1, 10))]
    assert safe_get(seq, random.randint(-10, -2)) is None
    assert safe_get(seq, random.randint(len(seq), len(seq) + 10)) is None
    idx = random.randint(0, len(seq) - 1)
    assert safe_get(seq, idx) == seq[idx]


def test_sort_spans():
    spans = []
    start_window = 2
    start_loc = 0
    possible_length = 5
    for _ in range(random.randint(1, 10)):
        span_start = random.randint(0, start_window) + start_loc
        span_length = random.randint(1, possible_length)
        span_end = span_start + span_length
        span = Span(type=random_string(), start=span_start, end=span_end, tokens=tuple(range(span_start, span_end)))
        spans.append(span)
    shuffed = deepcopy(spans)
    random.shuffle(shuffed)
    assert sort_spans(shuffed) == spans


def test_sort_errors():
    errors = []
    start_window = 2
    start_loc = 0
    for _ in range(random.randint(1, 10)):
        error_loc = random.randint(0, start_window) + start_loc
        start_loc = error_loc
        error = Error(error_loc, random_string(), random_string(), random_string(), random_string(),)
        errors.append(error)
    shuffed = deepcopy(errors)
    random.shuffle(shuffed)
    assert sort_errors(shuffed) == errors
