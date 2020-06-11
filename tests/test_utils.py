import random
from iobes.utils import safe_get, extract_function, extract_type
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
