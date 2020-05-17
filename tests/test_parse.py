from iobes.parse import (
    parse_spans_iob,
    parse_spans_bio,
    parse_spans_iobes,
    parse_spans_bilou,
    parse_spans_bmeow,
)
from utils import (
    generate_spans,
    generate_iob,
    generate_bio,
    generate_iobes,
    generate_bilou,
    generate_bmeow,
)


TRIALS = 100


def test_parse_iob():
    def test():
        spans, length = generate_spans()
        tags = generate_iob(spans, length)
        assert parse_spans_iob(tags) == spans

    for _ in range(TRIALS):
        test()


def test_parse_bio():
    def test():
        spans, length = generate_spans()
        tags = generate_bio(spans, length)
        assert parse_spans_bio(tags) == spans

    for _ in range(TRIALS):
        test()


def test_parse_iobes():
    def test():
        spans, length = generate_spans()
        tags = generate_iobes(spans, length)
        assert parse_spans_iobes(tags) == spans

    for _ in range(TRIALS):
        test()


def test_parse_bilou():
    def test():
        spans, length = generate_spans()
        tags = generate_bilou(spans, length)
        assert parse_spans_bilou(tags) == spans

    for _ in range(TRIALS):
        test()


def test_parse_bmeow():
    def test():
        spans, length = generate_spans()
        tags = generate_bmeow(spans, length)
        assert parse_spans_bmeow(tags) == spans

    for _ in range(TRIALS):
        test()
