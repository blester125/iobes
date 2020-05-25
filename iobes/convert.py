from typing import List
from itertools import chain
from iobes import TokenFunction
from iobes.utils import extract_type, extract_function, replace_prefix


def iob_to_bio(tags: List[str]) -> List[str]:
    new_tags = []
    prev_type = TokenFunction.OUTSIDE
    for token in tags:
        func = extract_function(token)
        _type = extract_type(token)
        # `I-` tags at the beginning need to be converted
        if func == TokenFunction.INSIDE:
            # If we are after an `O` we are the start of an entity and need to switch to `B-`
            # If we are after an `I-` or `B-` of a different type we are a new entity
            if prev_type == TokenFunction.OUTSIDE or _type != prev_type:
                token = f"{TokenFunction.BEGIN}-{_type}"
            # If we are after one of the same type then we are part of that entity and don't change
        # `B-` tags are passed through as is
        new_tags.append(token)
        prev_type = _type
    return new_tags


def iob_to_iobes(tags: List[str]) -> List[str]:
    return bio_to_iobes(iob_to_bio(tags))


def iob_to_bilou(tags: List[str]) -> List[str]:
    return iobes_to_bilou(iob_to_iobes(tags))


def iob_to_bmeow(tags: List[str]) -> List[str]:
    return iobes_to_bmeow(iob_to_iobes(tags))


iob_to_bmewo = iob_to_bmeow


def bio_to_iob(tags: List[str]) -> List[str]:
    new_tags = []
    prev_type = TokenFunction.OUTSIDE
    for token in tags:
        _type = extract_type(token)
        func = extract_function(token)
        # We want to keep `B-`s that represent the transition between two entities of the same type
        # and convert the rest of them to `I-`s
        if func == TokenFunction.BEGIN:
            if prev_type != _type:
                token = f"{TokenFunction.INSIDE}-{_type}"
        # `I-` tags are passed through
        new_tags.append(token)
        prev_type = _type
    return new_tags


def bio_to_iobes(tags: List[str]) -> List[str]:
    new_tags = []
    for c, n in zip(tags, chain(tags[1:], [TokenFunction.OUTSIDE])):
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
        new_tags.append(token)
    return new_tags


def bio_to_bilou(tags: List[str]) -> List[str]:
    return iobes_to_bilou(bio_to_iobes(tags))


def bio_to_bmeow(tags: List[str]) -> List[str]:
    return iobes_to_bmeow(bio_to_iobes(tags))


bio_to_bmewo = bio_to_bmeow


def iobes_to_iob(tags: List[str]) -> List[str]:
    return bio_to_iob(iobes_to_bio(tags))


def iobes_to_bio(tags: List[str]) -> List[str]:
    return list(
        map(
            lambda x: replace_prefix(
                replace_prefix(x, TokenFunction.END, TokenFunction.INSIDE), TokenFunction.SINGLE, TokenFunction.BEGIN
            ),
            tags,
        )
    )


def iobes_to_bilou(tags: List[str]) -> List[str]:
    return [iobes_to_bilou_token(t) for t in tags]


def iobes_to_bmeow(tags: List[str]) -> List[str]:
    return [iobes_to_bmeow_token(s) for s in tags]


iobes_to_bmewo = iobes_to_bmeow


def bilou_to_iob(tags: List[str]) -> List[str]:
    return iobes_to_iob(bilou_to_iobes(tags))


def bilou_to_bio(tags: List[str]) -> List[str]:
    return iobes_to_bio(bilou_to_iobes(tags))


def bilou_to_iobes(tags: List[str]) -> List[str]:
    return [bilou_to_iobes_token(t) for t in tags]


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
    return [bmeow_to_iobes_token(t) for t in tags]


bmewo_to_iobes = bmeow_to_iobes


def bmeow_to_bilou(tags: List[str]) -> List[str]:
    return iobes_to_bilou(bmeow_to_iobes(tags))


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
