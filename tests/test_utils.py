import random
from iobes.utils import safe_get, replace_prefix, extract_function, extract_type
from utils import random_string


def test_extract_type():
    func, _type = random_string(), random_string()
    tag = "-".join([func, _type])
    assert extract_type(tag) == _type


def test_extract_function():
    func, _type = random_string(), random_string()
    tag = "-".join([func, _type])
    assert extract_function(tag) == func


def test_replace_prefix():
    base = random_string(min_length=10, max_length=25)
    prefix = base[0]
    while base.startswith(prefix):
        prefix = random_string()
    new = random_string()
    assert replace_prefix(base, prefix, new) == base
    assert replace_prefix(prefix + base, prefix, new) == new + base
    pivot = random.randint(1, len(base) - 1)
    middle = base[:pivot] + prefix + base[pivot:]
    assert replace_prefix(middle, prefix, "") == middle


def test_replace_safe_get():
    seq = [random_string() for _ in range(random.randint(1, 10))]
    assert safe_get(seq, random.randint(-10, -2)) is None
    assert safe_get(seq, random.randint(len(seq), len(seq) + 10)) is None
    idx = random.randint(0, len(seq) - 1)
    assert safe_get(seq, idx) == seq[idx]
