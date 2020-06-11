from typing import List, Tuple, Callable
from itertools import chain
from iobes import TokenFunction, Span, Error
from iobes.parse import (
    parse_spans_iob_with_errors,
    parse_spans_bio_with_errors,
    parse_spans_iobes_with_errors,
    parse_spans_bilou_with_errors,
    parse_spans_bmeow_with_errors,
)
from iobes.write import (
    write_iob_tags,
    write_bio_tags,
    write_iobes_tags,
    write_bilou_tags,
    write_bmeow_tags,
)


def convert_tags(
    tags: List[str],
    parse_function: Callable[[List[str]], Tuple[List[Span], List[Error]]],
    write_function: Callable[[List[Span], int], List[str]],
) -> List[str]:
    spans, errors = parse_function(tags)
    if errors:
        error_string = "\n".join(str(e) for e in errors)
        raise ValueError(f"Found errors in the tag sequence, cannot be converted. Errors: {error_string}")
    return write_function(spans, len(tags))


def iob_to_bio(tags: List[str]) -> List[str]:
    return convert_tags(tags, parse_spans_iob_with_errors, write_bio_tags)


def iob_to_iobes(tags: List[str]) -> List[str]:
    return bio_to_iobes(iob_to_bio(tags))


def iob_to_bilou(tags: List[str]) -> List[str]:
    return iobes_to_bilou(iob_to_iobes(tags))


def iob_to_bmeow(tags: List[str]) -> List[str]:
    return iobes_to_bmeow(iob_to_iobes(tags))


iob_to_bmewo = iob_to_bmeow


def bio_to_iob(tags: List[str]) -> List[str]:
    return convert_tags(tags, parse_spans_bio_with_errors, write_iob_tags)


def bio_to_iobes(tags: List[str]) -> List[str]:
    return convert_tags(tags, parse_spans_bio_with_errors, write_iobes_tags)


def bio_to_bilou(tags: List[str]) -> List[str]:
    return iobes_to_bilou(bio_to_iobes(tags))


def bio_to_bmeow(tags: List[str]) -> List[str]:
    return iobes_to_bmeow(bio_to_iobes(tags))


bio_to_bmewo = bio_to_bmeow


def iobes_to_iob(tags: List[str]) -> List[str]:
    return bio_to_iob(iobes_to_bio(tags))


def iobes_to_bio(tags: List[str]) -> List[str]:
    return convert_tags(tags, parse_spans_iobes_with_errors, write_bio_tags)


def iobes_to_bilou(tags: List[str]) -> List[str]:
    return convert_tags(tags, parse_spans_iobes_with_errors, write_bilou_tags)


def iobes_to_bmeow(tags: List[str]) -> List[str]:
    return convert_tags(tags, parse_spans_iobes_with_errors, write_bmeow_tags)


iobes_to_bmewo = iobes_to_bmeow


def bilou_to_iob(tags: List[str]) -> List[str]:
    return iobes_to_iob(bilou_to_iobes(tags))


def bilou_to_bio(tags: List[str]) -> List[str]:
    return iobes_to_bio(bilou_to_iobes(tags))


def bilou_to_iobes(tags: List[str]) -> List[str]:
    return convert_tags(tags, parse_spans_bilou_with_errors, write_iobes_tags)


def bilou_to_bmeow(tags: List[str]) -> List[str]:
    return iobes_to_bmeow(bilou_to_iobes(tags))


bilou_to_bmewo = bilou_to_bmeow


def bmeow_to_iob(tags: List[str]) -> List[str]:
    return iobes_to_iob(bmeow_to_iobes(tags))


bmewo_to_iob = bmeow_to_iob


def bmeow_to_bio(tags: List[str]) -> List[str]:
    return iobes_to_bio(bmeow_to_iobes(tags))


bmewo_to_bio = bmeow_to_bio


def bmeow_to_iobes(tags: List[str]) -> List[str]:
    return convert_tags(tags, parse_spans_bmeow_with_errors, write_iobes_tags)


bmewo_to_iobes = bmeow_to_iobes


def bmeow_to_bilou(tags: List[str]) -> List[str]:
    return iobes_to_bilou(bmeow_to_iobes(tags))


bmewo_to_bilou = bmeow_to_bilou
