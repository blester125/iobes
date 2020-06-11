from itertools import chain, permutations
from typing import List, Tuple, NamedTuple, Dict, Set
from iobes import SpanEncoding, TokenFunction, SpanFormat, IOB, BIO, IOBES, BILOU, BMEOW
from iobes.utils import extract_function, extract_type


class Transition(NamedTuple):
    source: str
    target: str
    valid: bool


def transitions_to_tuple_map(transitions: List[Transition]) -> Dict[Tuple[str, str], bool]:
    return {(src, tgt): valid for src, tgt, valid in transitions}


def transitions_to_map(transitions: List[Transition]) -> Dict[str, Dict[str, bool]]:
    mapping = {}
    for src, tgt, valid in transitions:
        to = mapping.setdefault(src, {})
        to[tgt] = valid
    return mapping


def transitions_to_mask(transitions: List[Transition], vocabulary: Dict[str, int]) -> 'np.ndarray':
    try:
        import numpy as np
    except ImportError:
        LOGGER.critical("Could not import the `numpy` library which is needed to create a transition mask. Use `pip install iobes[mask] to include the optional `numpy` dependency.")
    mask = np.zeros((len(vocabulary), len(vocabulary)))
    for src, tgt, value in transitions:
        if value:
            mask[vocabulary[src], vocabulary[tgt]] = 1
    return mask


def transitions_legality(
    tokens: Set[str], span_type: SpanEncoding, start: str = TokenFunction.GO, end: str = TokenFunction.EOS
) -> List[Transition]:
    if span_type is SpanEncoding.IOB:
        return iob_transitions_legality(tokens, start, end)
    if span_type is SpanEncoding.BIO:
        return bio_transitions_legality(tokens, start, end)
    if span_type is SpanEncoding.IOBES:
        return iobes_transitions_legality(tokens, start, end)
    if span_type is SpanEncoding.BILOU:
        return bilou_transitions_legality(tokens, start, end)
    if span_type is SpanEncoding.BMEOW or span_type is SpanEncoding.BMEWO:
        return bmeow_transitions_legality(tokens, start, end)
    if span_type is SpanEncoding.TOKEN:
        return token_transitions_legality(tokens, start, end)
    raise ValueError(f"Unknown SpanEncoding Scheme, got: `{span_type}`")


def token_transitions_legality(tokens: Set[str], start: str = TokenFunction.GO, end: str = TokenFunction.EOS) -> List[Transition]:
    transitions = []
    for src, tgt in permutations(tokens, 2):
        transitions.append(Transition(src, tgt, True))
    for token in tokens:
        transitions.append(Transition(token, token, True))
        transitions.append(Transition(start, token, True))
        transitions.append(Transition(token, start, False))
        transitions.append(Transition(token, end, True))
        transitions.append(Transition(end, token, False))
    return transitions


def iob_transitions_legality(tokens: Set[str], start: str = TokenFunction.GO, end: str = TokenFunction.EOS) -> List[Transition]:
    transitions = []
    for src in chain(tokens, [start, end]):
        src_func = extract_function(src)
        src_type = extract_type(src)
        for tgt in chain(tokens, [start, end]):
            tgt_func = extract_function(tgt)
            tgt_type = extract_type(tgt)
            # Can't transition to start
            if tgt == start:
                transitions.append(Transition(src, tgt, False))
                continue
            # Can't transition from start
            if src == end:
                transitions.append(Transition(src, tgt, False))
                continue
            # Can't transition from start to B because B needs to be between two spans of the same type
            elif src == start:
                if tgt_func == TokenFunction.BEGIN:
                    transitions.append(Transition(src, tgt, False))
                    continue
            elif src_func == TokenFunction.BEGIN:
                # Can only go from B to B of the same type
                if tgt_func == TokenFunction.BEGIN:
                    if src_type != tgt_type:
                        transitions.append(Transition(src, tgt, False))
                        continue
            elif src_func == TokenFunction.INSIDE:
                # Can only go from I to B of the same type
                if tgt_func == TokenFunction.BEGIN:
                    if src_type != tgt_type:
                        transitions.append(Transition(src, tgt, False))
                        continue
            elif src_func == TokenFunction.OUTSIDE:
                # Can't start a span with B unless preceded by another span
                if tgt_func == TokenFunction.BEGIN:
                    transitions.append(Transition(src, tgt, False))
                    continue
            transitions.append(Transition(src, tgt, True))
    return transitions


def bio_transitions_legality(tokens: Set[str], start: str = TokenFunction.GO, end: str = TokenFunction.EOS) -> List[Transition]:
    transitions = []
    for src in chain(tokens, [start, end]):
        src_func = extract_function(src)
        src_type = extract_type(src)
        for tgt in chain(tokens, [start, end]):
            tgt_func = extract_function(tgt)
            tgt_type = extract_type(tgt)
            # Can't transition to start
            if tgt == start:
                transitions.append(Transition(src, tgt, False))
                continue
            # Can't transition from end
            if src == end:
                transitions.append(Transition(src, tgt, False))
                continue
            elif src == start:
                # Can't go from start to an I
                if tgt_func == BIO.INSIDE:
                    transitions.append(Transition(src, tgt, False))
                    continue
            elif src_func == BIO.BEGIN:
                # Can only go from B to I of same type
                if tgt_func == BIO.INSIDE:
                    if src_type != tgt_type:
                        transitions.append(Transition(src, tgt, False))
                        continue
            elif src_func == BIO.INSIDE:
                # Can only go from I to I of same type
                if tgt_func == BIO.INSIDE:
                    if src_type != tgt_type:
                        transitions.append(Transition(src, tgt, False))
                        continue
            elif src_func == TokenFunction.OUTSIDE:
                # Can't start an entity with I
                if tgt_func == BIO.INSIDE:
                    transitions.append(Transition(src, tgt, False))
                    continue
            transitions.append(Transition(src, tgt, True))
    return transitions


def with_end_transitions_legality(tokens: Set[str], span_format: SpanFormat, start: str = TokenFunction.GO, end: str = TokenFunction.EOS) -> List[Transition]:
    transitions = []
    for src in chain(tokens, [start, end]):
        src_func = extract_function(src)
        src_type = extract_type(src)
        for tgt in chain(tokens, [start, end]):
            tgt_func = extract_function(tgt)
            tgt_type = extract_type(tgt)
            # Can't transition to start
            if tgt == start:
                transitions.append(Transition(src, tgt, False))
                continue
            # Can't transition from end
            if src == end:
                transitions.append(Transition(src, tgt, False))
                continue
            elif src == start:
                # Can't start span with I or E
                if tgt_func in (span_format.INSIDE, span_format.END):
                    transitions.append(Transition(src, tgt, False))
                    continue
            elif src_func == span_format.BEGIN:
                # Can't go from B to B, S, or O because we didn't close the entity
                if tgt_func in (span_format.BEGIN, span_format.SINGLE, TokenFunction.OUTSIDE) or tgt_func == end:
                    transitions.append(Transition(src, tgt, False))
                    continue
                # Can only go from B to I or E of the same type
                elif tgt_func in (span_format.INSIDE, span_format.END):
                    if src_type != tgt_type:
                        transitions.append(Transition(src, tgt, False))
                        continue
            elif src_func == span_format.INSIDE:
                # Can't from from I to B, S, or O because we didin't close the entity
                if tgt_func in (span_format.BEGIN, span_format.SINGLE, TokenFunction.OUTSIDE) or tgt == end:
                    transitions.append(Transition(src, tgt, False))
                    continue
                # Can only go from I to I or E of the same Type
                elif tgt_func in (span_format.INSIDE, span_format.END):
                    if src_type != tgt_type:
                        transitions.append(Transition(src, tgt, False))
                        continue
            elif src_func in (span_format.END, span_format.SINGLE, TokenFunction.OUTSIDE):
                # Going from outside an entity (or ending it) to one that was inside the entity (I/E) is illegal
                if tgt_func in (span_format.INSIDE, span_format.END):
                    transitions.append(Transition(src, tgt, False))
                    continue
            # Other transitions are allowed
            transitions.append(Transition(src, tgt, True))
    return transitions


def iobes_transitions_legality(tokens: Set[str], start: str = TokenFunction.GO, end: str = TokenFunction.EOS) -> List[Transition]:
    return with_end_transtitions_legality(tokens, IOBES, start, end)


def bilou_transitions_legality(tokens: Set[str], start: str = TokenFunction.GO, end: str = TokenFunction.EOS) -> List[Transition]:
    return with_end_transtitions_legality(tokens, BILOU, start, end)


def bmeow_transitions_legality(tokens: Set[str], start: str = TokenFunction.GO, end: str = TokenFunction.EOS) -> List[Transition]:
    return with_end_transtitions_legality(tokens, BMEOW, start, end)


bmewo_transitions_legality = bmeow_transitions_legality
