from typing import List
from itertools import chain
from iobes import TokenFunction
from iobes.utils import extract_type, extract_function, replace_prefix


def iob_to_bio(seq: List[str]) -> List[str]:
    new_seq = []
    prev_type = TokenFunction.OUTSIDE
    for token in seq:
        func = extract_function(token)
        _type = extract_type(token)
        if func == TokenFunction.INSIDE:
            if prev_type == TokenFunction.OUTSIDE or _type != prev_type:
                token = f"{TokenFunction.BEGIN}-{_type}"
        new_seq.append(token)
        prev_type = _type
    return new


def iob_to_iobes(seq: List[str]) -> List[str]:
    return bio_to_iobes(iob_to_bio(seq))


def iob_to_bilou(seq: List[str]) -> List[str]:
    return iobes_to_bilou(iob_to_iobes(seq))


def iob_to_bmeow(seq: List[str]) -> List[str]:
    return iobes_to_bmeow(iob_to_iobes(seq))


iob_to_bmewo = iob_to_bmeow


def bio_to_iob(seq: List[str]) -> List[str]:
    new_seq = []
    prev_type = TokenFunction.OUTSIDE
    for token in seq:
        _type = extract_type(token)
        func = extract_function(token)
        if func == TokenFunction.BEGIN:
            if prev_type != _type:
                token = f"{TokenFunction.INSIDE}-{_type}"
        new_seq.append(token)
        prev_type = _type
    return new_seq


def bio_to_iobes(seq: List[str]) -> List[str]:
    new_seq = []
    for c, n in zip(seq, chain(seq[1:], [TokenFunction.OUTSIDE])):
        curr_func = extract_function(c)
        curr_type = extract_type(c)
        next_func = extract_function(n)
        next_type = extract_type(n)
        if curr_func == TokenFunction.BEGIN:
            if next_func == TokenFunction.INSIDE and next_type == curr_type:
                token = c
            else:
                token = f"{TokenFunction.SINGLE}-{curr_type}"
        elif curr_func == TokenFunction.INSIDE:
            if next_func == TokenFunction.INSIDE and next_type == curr_type:
                token = c
            else:
                token = f"{TokenFunction.END}-{curr_type}"
        else:
            token = c
        new_seq.append(token)
    return new_seq


def bio_to_bilou(seq: List[str]) -> List[str]:
    return iobes_to_bilou(bio_to_iobes(seq))


def bio_to_bmeow(seq: List[str]) -> List[str]:
    return iobes_to_bmeow(bio_to_iobes(seq))


bio_to_bmewo = bio_to_bmeow


def iobes_to_iob(seq: List[str]) -> List[str]:
    return bio_to_iob(iobes_to_bio(seq))


def iobes_to_bio(seq: List[str]) -> List[str]:
    return list(
        map(
            lambda x: replace_prefix(
                replace_prefix(x, TokenFunction.END, TokenFunction.INSIDE), TokenFunction.SINGLE, TokenFunction.BEGIN
            ),
            seq,
        )
    )


def iobes_to_bilou(seq: List[str]) -> List[str]:
    return [iobes_to_bilou_token(t) for t in seq]


def iobes_to_bmeow(seq: List[str]) -> List[str]:
    return [iobes_to_bmeow_token(s) for s in seq]


iobes_to_bmewo = iobes_to_bmeow


def bilou_to_iob(seq: List[str]) -> List[str]:
    return iobes_to_iob(bilou_to_iobes(seq))


def bilou_to_bio(seq: List[str]) -> List[str]:
    return iobes_to_bio(bilou_to_iobes(seq))


def bilou_to_iobes(seq: List[str]) -> List[str]:
    return [bilou_to_iobes_token(t) for t in seq]


def bilou_to_bmeow(seq: List[str]) -> List[str]:
    return iobes_to_bmeow(bilou_to_iobes(seq))


bilou_to_bmewo = bilou_to_bmeow


def bmeow_to_iob(seq: List[str]) -> List[str]:
    return iobes_to_iob(bmeow_to_iobes(seq))


bmewo_to_iob = bmeow_to_iob


def bmeow_to_bio(seq: List[str]) -> List[str]:
    return iobes_to_bio(bmeow_to_iobes(seq))


bmewo_to_bio = bmeow_to_bio


def bmeow_to_iobes(seq: List[str]) -> List[str]:
    return [bmeow_to_iobes_token(t) for t in seq]


bmewo_to_iobes = bmeow_to_iobes


def bmeow_to_bilou(sewq: List[str]) -> List[str]:
    return iobes_to_bilou(bmeow_to_iobes(seq))


bmewo_to_bilou = bmeow_to_bilou


def bilou_to_iobes_token(token: str) -> str:
    func = extract_function(token)
    _type = extract_type(token)
    if func == TokenFunction.LAST:
        return f"{TokenFunction.END}-{_type}"
    if func == TokenFunction.UNIT:
        return f"{TokenFunction.SINGLE}-{_type}"
    return token


def iobes_to_bilou_token(token: str) -> str:
    func = extract_function(token)
    _type = extract_type(token)
    if func == TokenFunction.END:
        return f"{TokenFunction.LAST}-{_type}"
    if func == TokenFunction.SINGLE:
        return f"{TokenFunction.UNIT}-{_type}"
    return token


def iobes_to_bmeow_token(token: str) -> str:
    func = extract_function(token)
    _type = extract_type(token)
    if func == TokenFunction.INSIDE:
        return f"{TokenFunction.MIDDLE}-{_type}"
    if func == TokenFunction.SINGLE:
        return f"{TokenFunction.WHOLE}-{_type}"
    return token


iobes_to_bmewo_token = iobes_to_bmeow


def bmeow_to_iobes_token(token: str) -> str:
    func = extract_function(token)
    _type = extract_type(token)
    if func == TokenFunction.MIDDLE:
        return f"{TokenFunction.INSIDE}-{_type}"
    if func == TokenFunction.WHOLE:
        return f"{TokenFunction.SINGLE}-{_type}"
    return token


bmewo_to_iobes_token = bmeow_to_iobes_token


def bilou_to_bmeow_token(token: str) -> str:
    return iobes_to_bmeow_token(bilou_to_iobes_token(token))


bilou_to_bmewo_token = bilou_to_bmeow_token


def bmeow_to_bilou_token(token: str) -> str:
    return iobes_to_bilou_token(bmwow_to_iobes_token(token))


bmewo_to_bilou_token = bmeow_to_bilou_token
