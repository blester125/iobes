from typing import List
from itertools import chain
from iobes import Function
from iobes.utils import extract_type, extract_function, replace_prefix


def iob_to_bio(seq: List[str]) -> List[str]:
    new_seq = []
    prev_type = Function.OUTSIDE
    for token in seq:
        func = extract_function(token)
        _type = extract_type(token)
        if func == Function.INSIDE:
            if prev_type == Function.OUTSIDE or _type != prev_type:
                token = f"{Function.BEGIN}-{_type}"
        new_seq.append(token)
        prev_type = _type
    return new


def iob_to_iobes(seq: List[str]) -> List[str]:
    return bio_to_iobes(iob_to_bio(seq))


def iob_to_bilou(seq: List[str]) -> List[str]:
    return iobes_to_bilou(iob_to_iobes(seq))


def iob_to_bmeow(seq: List[str]) -> List[str]:
    return iobes_to_bmeow(iob_to_iobes(seq))


def bio_to_iob(seq: List[str]) -> List[str]:
    new_seq = []
    prev_type = Function.OUTSIDE
    for token in seq:
        _type = extract_type(token)
        func = extract_function(token)
        if func == Function.BEGIN:
            if prev_type != _type:
                token = f"{Function.INSIDE}-{_type}"
        new_seq.append(token)
        prev_type = _type
    return new_seq


def bio_to_iobes(seq: List[str]) -> List[str]:
    new_seq = []
    for c, n in zip(seq, chain(seq[1:], [Function.OUTSIDE])):
        curr_func = extract_function(c)
        curr_type = extract_type(c)
        next_func = extract_function(n)
        next_type = extract_type(n)
        if curr_func == Function.BEGIN:
            if next_func == Function.INSIDE and next_type == curr_type:
                token = c
            else:
                token = f"{Function.SINGLE}-{curr_type}"
        elif curr_func == Function.INSIDE:
            if next_func == Function.INSIDE and next_type == curr_type:
                token = c
            else:
                token = f"{Function.END}-{curr_type}"
        else:
            token = c
        new_seq.append(token)
    return new_seq


def bio_to_bilou(seq: List[str]) -> List[str]:
    return iobes_to_bilou(bio_to_iobes(seq))


def bio_to_bmeow(seq: List[str]) -> List[str]:
    return iobes_to_bmeow(bio_to_iobes(seq))


def iobes_to_iob(seq: List[str]) -> List[str]:
    return bio_to_iob(iobes_to_bio(seq))


def iobes_to_bio(seq: List[str]) -> List[str]:
    return list(
        map(
            lambda x: replace_prefix(replace_prefix(x, Function.END, Function.INSIDE), Function.SINGLE, Function.BEGIN),
            seq,
        )
    )


def iobes_to_bilou(seq: List[str]) -> List[str]:
    new_seq = []
    for token in seq:
        func = extract_function(token)
        _type = extract_type(token)
        if func == Function.END:
            token = f"{Function.LAST}-{_type}"
        elif func == Function.SINGLE:
            token = f"{Function.UNIT}-{_type}"
        new_seq.append(token)
    return new_seq


def iobes_to_bmeow(seq: List[str]) -> List[str]:
    new_seq = []
    for token in seq:
        func = extract_function(token)
        _type = extract_type(token)
        if func == Function.INSIDE:
            token = f"{Function.MIDDLE}-{_type}"
        elif func == Function.SINGLE:
            token = f"{Function.WHOLE}-{_type}"
        new_seq.append(token)
    return new_seq


def bilou_to_iob(seq: List[str]) -> List[str]:
    return iobes_to_iob(bilou_to_iobes(seq))


def bilou_to_bio(seq: List[str]) -> List[str]:
    return iobes_to_bio(bilou_to_iobes(seq))


def bilou_to_iobes(seq: List[str]) -> List[str]:
    new_seq = []
    for token in seq:
        func = extract_function(token)
        _type = extract_type(token)
        if func == Function.LAST:
            token = f"{Function.END}-{_type}"
        elif func == Function.UNIT:
            token = f"{Function.SINGLE}-{_type}"
        new_seq.append(token)
    return new_seq


def bilou_to_bmeow(seq: List[str]) -> List[str]:
    return iobes_to_bmeow(bilou_to_iobes(seq))


def bmeow_to_iob(seq: List[str]) -> List[str]:
    return iobes_to_iob(bmeow_to_iobes(seq))


def bmeow_to_bio(seq: List[str]) -> List[str]:
    return iobes_to_bio(bmeow_to_iobes(seq))


def bmeow_to_iobes(seq: List[str]) -> List[str]:
    new_seq = []
    for token in seq:
        func = extract_function(token)
        _type = extract_type(token)
        if func == Function.MIDDLE:
            token = f"{Function.INSIDE}-{_type}"
        elif func == Function.WHOLE:
            token = f"{Function.SINGLE}-{_type}"
        new_seq.append(token)
    return new_seq


def bmeow_to_bilou(sewq: List[str]) -> List[str]:
    return iobes_to_bilou(bmeow_to_iobes(seq))
