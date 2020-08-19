from itertools import chain
from typing import List, Tuple, Callable
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
    """Convert tags from one format to another.

    Args:
        tags: The tags that we are converting.
        parse_function: A function that parses tags into spans.
        write_function: A function the turns spans into a list of tags.

    Raises:
        ValueError: If there were errors in the tag formatting.

    Returns:
        The list of tags in the new format.
    """
    spans, errors = parse_function(tags)
    if errors:
        error_string = "\n".join(str(e) for e in errors)
        raise ValueError(f"Found errors in the tag sequence, cannot be converted. Errors: {error_string}")
    return write_function(spans, length=len(tags))


def iob_to_bio(tags: List[str]) -> List[str]:
    """Convert IOB tags to the BIO format.

    Args:
        tags: The IOB tags we are converting

    Raises:
        ValueError: If there were errors in the IOB formatting of the input.

    Returns:
        Tags that produce the same spans in the BIO format.
    """
    return convert_tags(tags, parse_spans_iob_with_errors, write_bio_tags)


def iob_to_iobes(tags: List[str]) -> List[str]:
    """Convert IOB tags to the IOBES format.

    Args:
        tags: The IOB tags we are converting

    Raises:
        ValueError: If there were errors in the IOB formatting of the input.

    Returns:
        Tags that produce the same spans in the IOBES format.
    """
    return bio_to_iobes(iob_to_bio(tags))


def iob_to_bilou(tags: List[str]) -> List[str]:
    """Convert IOB tags to the BILOU format.

    Args:
        tags: The IOB tags we are converting

    Raises:
        ValueError: If there were errors in the IOB formatting of the input.

    Returns:
        Tags that produce the same spans in the BILOU format.
    """
    return iobes_to_bilou(iob_to_iobes(tags))


def iob_to_bmeow(tags: List[str]) -> List[str]:
    """Convert IOB tags to the BMEOW format.

    Args:
        tags: The IOB tags we are converting

    Raises:
        ValueError: If there were errors in the IOB formatting of the input.

    Returns:
        Tags that produce the same spans in the BMEOW format.
    """
    return iobes_to_bmeow(iob_to_iobes(tags))


def iob_to_bmewo(tags: List[str]) -> List[str]:
    """Convert IOB tags to the BMEWO format.

    Note:
        Alias for :py:func:`~iobes.convert.iob_to_bmeow`.

    Args:
        tags: The IOB tags we are converting

    Raises:
        ValueError: If there were errors in the IOB formatting of the input.

    Returns:
        Tags that produce the same spans in the BMEOW format.
    """
    return iob_to_bmeow(tags)


def bio_to_iob(tags: List[str]) -> List[str]:
    """Convert BIO tags to the IOB format.

    Args:
        tags: The BIO tags we are converting

    Raises:
        ValueError: If there were errors in the BIO formatting of the input.

    Returns:
        Tags that produce the same spans in the IOB format.
    """
    return convert_tags(tags, parse_spans_bio_with_errors, write_iob_tags)


def bio_to_iobes(tags: List[str]) -> List[str]:
    """Convert BIO tags to the IOBES format.

    Args:
        tags: The BIO tags we are converting

    Raises:
        ValueError: If there were errors in the BIO formatting of the input.

    Returns:
        Tags that produce the same spans in the IOBES format.
    """
    return convert_tags(tags, parse_spans_bio_with_errors, write_iobes_tags)


def bio_to_bilou(tags: List[str]) -> List[str]:
    """Convert BIO tags to the BILOU format.

    Args:
        tags: The BIO tags we are converting

    Raises:
        ValueError: If there were errors in the BIO formatting of the input.

    Returns:
        Tags that produce the same spans in the BILOU format.
    """
    return iobes_to_bilou(bio_to_iobes(tags))


def bio_to_bmeow(tags: List[str]) -> List[str]:
    """Convert BIO tags to the BMEOW format.

    Args:
        tags: The BIO tags we are converting

    Raises:
        ValueError: If there were errors in the BIO formatting of the input.

    Returns:
        Tags that produce the same spans in the BMEOW format.
    """
    return iobes_to_bmeow(bio_to_iobes(tags))


def bio_to_bmewo(tags: List[str]) -> List[str]:
    """Convert BIO tags to the BMEWO format.

    Note:
        Alias for :py:func:`~iobes.convert.bio_to_bmeow`

    Args:
        tags: The BIO tags we are converting

    Raises:
        ValueError: If there were errors in the BIO formatting of the input.

    Returns:
        Tags that produce the same spans in the BMEWO format.
    """
    return bio_to_bmeow(tags)


def iobes_to_iob(tags: List[str]) -> List[str]:
    """Convert IOBES tags to the IOB format.

    Args:
        tags: The IOBES tags we are converting

    Raises:
        ValueError: If there were errors in the IOBES formatting of the input.

    Returns:
        Tags that produce the same spans in the IOB format.
    """
    return bio_to_iob(iobes_to_bio(tags))


def iobes_to_bio(tags: List[str]) -> List[str]:
    """Convert IOBES tags to the BIO format.

    Args:
        tags: The IOBES tags we are converting

    Raises:
        ValueError: If there were errors in the IOBES formatting of the input.

    Returns:
        Tags that produce the same spans in the BIO format.
    """
    return convert_tags(tags, parse_spans_iobes_with_errors, write_bio_tags)


def iobes_to_bilou(tags: List[str]) -> List[str]:
    """Convert IOBES tags to the BILOU format.

    Args:
        tags: The IOBES tags we are converting

    Raises:
        ValueError: If there were errors in the IOBES formatting of the input.

    Returns:
        Tags that produce the same spans in the BILOU format.
    """
    return convert_tags(tags, parse_spans_iobes_with_errors, write_bilou_tags)


def iobes_to_bmeow(tags: List[str]) -> List[str]:
    """Convert IOBES tags to the BMEOW format.

    Args:
        tags: The IOBES tags we are converting

    Raises:
        ValueError: If there were errors in the IOBES formatting of the input.

    Returns:
        Tags that produce the same spans in the BMEOW format.
    """
    return convert_tags(tags, parse_spans_iobes_with_errors, write_bmeow_tags)


def iobes_to_bmewo(tags: List[str]) -> List[str]:
    """Convert IOBES tags to the BMEWO format.

    Note:
        Alias for :py:func:`~iobes.convert.iobes_to_bmeow`

    Args:
        tags: The IOBES tags we are converting

    Raises:
        ValueError: If there were errors in the IOBES formatting of the input.

    Returns:
        Tags that produce the same spans in the BMEWO format.
    """
    return iobes_to_bmeow(tags)


def bilou_to_iob(tags: List[str]) -> List[str]:
    """Convert BILOU tags to the IOB format.

    Args:
        tags: The BILOU tags we are converting

    Raises:
        ValueError: If there were errors in the BILOU formatting of the input.

    Returns:
        Tags that produce the same spans in the IOB format.
    """
    return convert_tags(tags, parse_spans_bilou_with_errors, write_iob_tags)


def bilou_to_bio(tags: List[str]) -> List[str]:
    """Convert BILOU tags to the BIO format.

    Args:
        tags: The BILOU tags we are converting

    Raises:
        ValueError: If there were errors in the BILOU formatting of the input.

    Returns:
        Tags that produce the same spans in the BIO format.
    """
    return convert_tags(tags, parse_spans_bilou_with_errors, write_bio_tags)


def bilou_to_iobes(tags: List[str]) -> List[str]:
    """Convert BILOU tags to the IOBES format.

    Args:
        tags: The BILOU tags we are converting

    Raises:
        ValueError: If there were errors in the BILOU formatting of the input.

    Returns:
        Tags that produce the same spans in the IOBES format.
    """
    return convert_tags(tags, parse_spans_bilou_with_errors, write_iobes_tags)


def bilou_to_bmeow(tags: List[str]) -> List[str]:
    """Convert BILOU tags to the BMEOW format.

    Args:
        tags: The BILOU tags we are converting

    Raises:
        ValueError: If there were errors in the BILOU formatting of the input.

    Returns:
        Tags that produce the same spans in the BMEOW format.
    """
    return convert_tags(tags, parse_spans_bilou_with_errors, write_bmeow_tags)


def bilou_to_bmewo(tags: List[str]) -> List[str]:
    """Convert BILOU tags to the BMEWO format.

    Note:
        Alias for :py:func:`~iobes.convert.bilou_to_bmeow`

    Args:
        tags: The BILOU tags we are converting

    Raises:
        ValueError: If there were errors in the BILOU formatting of the input.

    Returns:
        Tags that produce the same spans in the BMEWO format.
    """
    return bilou_to_bmeow(tags)


def bmeow_to_iob(tags: List[str]) -> List[str]:
    """Convert BMEOW tags to the IOB format.

    Args:
        tags: The BMEOW tags we are converting

    Raises:
        ValueError: If there were errors in the BMEOW formatting of the input.

    Returns:
        Tags that produce the same spans in the IOB format.
    """
    return convert_tags(tags, parse_spans_bmeow_with_errors, write_iob_tags)


def bmeow_to_bio(tags: List[str]) -> List[str]:
    """Convert BMEOW tags to the BIO format.

    Args:
        tags: The BMEOW tags we are converting

    Raises:
        ValueError: If there were errors in the BMEOW formatting of the input.

    Returns:
        Tags that produce the same spans in the BIO format.
    """
    return convert_tags(tags, parse_spans_bmeow_with_errors, write_bio_tags)


def bmeow_to_iobes(tags: List[str]) -> List[str]:
    """Convert BMEOW tags to the IOBES format.

    Args:
        tags: The BMEOW tags we are converting

    Raises:
        ValueError: If there were errors in the BMEOW formatting of the input.

    Returns:
        Tags that produce the same spans in the IOBES format.
    """
    return convert_tags(tags, parse_spans_bmeow_with_errors, write_iobes_tags)


def bmeow_to_bilou(tags: List[str]) -> List[str]:
    """Convert BMEOW tags to the BILOU format.

    Args:
        tags: The BMEOW tags we are converting

    Raises:
        ValueError: If there were errors in the BMEOW formatting of the input.

    Returns:
        Tags that produce the same spans in the BILOU format.
    """
    return convert_tags(tags, parse_spans_bmeow_with_errors, write_bilou_tags)


def bmewo_to_iob(tags: List[str]) -> List[str]:
    """Convert BMEWO tags to the IOB format.

    Note:
        Alias for :py:func:`~iobes.convert.bmeow_to_iob`

    Args:
        tags: The BMEWO tags we are converting

    Raises:
        ValueError: If there were errors in the BMEWO formatting of the input.

    Returns:
        Tags that produce the same spans in the IOB format.
    """
    return bmeow_to_iob(tags)


def bmewo_to_bio(tags: List[str]) -> List[str]:
    """Convert BMEWO tags to the BIO format.

    Note:
        Alias for :py:func:`~iobes.convert.bmeow_to_bio`

    Args:
        tags: The BMEWO tags we are converting

    Raises:
        ValueError: If there were errors in the BMEWO formatting of the input.

    Returns:
        Tags that produce the same spans in the BIO format.
    """
    return bmeow_to_bio(tags)


def bmewo_to_iobes(tags: List[str]) -> List[str]:
    """Convert BMEWO tags to the IOBES format.

    Note:
        Alias for :py:func:`~iobes.convert.bmeow_to_iobes`

    Args:
        tags: The BMEWO tags we are converting

    Raises:
        ValueError: If there were errors in the BMEWO formatting of the input.

    Returns:
        Tags that produce the same spans in the IOBES format.
    """
    return bmeow_to_iobes(tags)


def bmewo_to_bilou(tags: List[str]) -> List[str]:
    """Convert BMEWO tags to the BILOU format.

    Note:
        Alias for :py:func:`~iobes.convert.bmeow_to_bilou`

    Args:
        tags: The BMEWO tags we are converting

    Raises:
        ValueError: If there were errors in the BMEWO formatting of the input.

    Returns:
        Tags that produce the same spans in the BILOU format.
    """
    return bmeow_to_bilou(tags)
