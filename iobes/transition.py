from itertools import chain, permutations
from typing import List, Tuple, NamedTuple, Dict, Set
from iobes import SpanEncoding, TokenFunction, SpanFormat, IOB, BIO, IOBES, BILOU, BMEOW
from iobes.utils import extract_function, extract_type


class Transition(NamedTuple):
    """A transition from one state to another.

    This includes information about whether the transition was legal or not.

    Args:
        source: The state you are starting at.
        target: The state you are going to.
        valid: Is this transition allowed by the encoding scheme?
    """

    source: str
    target: str
    valid: bool


def transitions_legality(
    tags: Set[str], span_type: SpanEncoding, start: str = TokenFunction.GO, end: str = TokenFunction.EOS
) -> List[Transition]:
    """Get the transition legality for some SpanEncoding format.

    Return a list of transitions and their legality based on the SpanEncoding schemes and
    the types of spans present.

    This is a convenience function that dispatches to span encoding specific implementations
    based on the span_type.

    Note:
        We include special tags that represent the start and end of sequences. These are
        special values that make downstream implementations of things like Conditional
        Random Fields (CRFs) `Lafferty et. al., 2001`__ and helps define constraints about
        what tags are allowed on the first and last token in a sequence. General rules around
        the start symbol is that nothing can transition to the start token and the legal targets
        of a transition from a start symbol is limited by the span encoding scheme. Similarly
        the end token cannot transition into anything else and what can transition to it is
        specified by the encoding scheme.

    Args:
        tags: The tags that we can assign to tokens.
        span_type: The span encoding format we are trying to use. Different formats impose different
            rules about which transitions are legal or not.
        start: A special tag representing the start of all sequences.
        end: A special tag representing the end of all sequences.

    Returns:
        The list of transitions.

    __ https://repository.upenn.edu/cgi/viewcontent.cgi?article=1162&context=cis_papers
    """
    if span_type is SpanEncoding.IOB:
        return iob_transitions_legality(tags, start, end)
    if span_type is SpanEncoding.BIO:
        return bio_transitions_legality(tags, start, end)
    if span_type is SpanEncoding.IOBES:
        return iobes_transitions_legality(tags, start, end)
    if span_type is SpanEncoding.BILOU:
        return bilou_transitions_legality(tags, start, end)
    if span_type is SpanEncoding.BMEOW or span_type is SpanEncoding.BMEWO:
        return bmeow_transitions_legality(tags, start, end)
    if span_type is SpanEncoding.TOKEN:
        return token_transitions_legality(tags, start, end)
    raise ValueError(f"Unknown SpanEncoding Scheme, got: `{span_type}`")


def token_transitions_legality(
    tags: Set[str], start: str = TokenFunction.GO, end: str = TokenFunction.EOS
) -> List[Transition]:
    """Get transition legality when processing tokens.

    Note:
        Token level annotations like Part of Speech Tagging don't have transition constrains
        defined by the span encoding scheme (because there is no span encoding scheme). This
        means that most every transition is allowed. The only illegal transitions are moving
        back to the special start token or leaving the end token.

    Args:
        tags: The tags that we can assign to tokens.
        start: A special tag representing the start of all sequences.
        end: A special tag representing the end of all sequences.

    Returns:
        The list of transitions.
    """
    transitions = []
    for src, tgt in permutations(tags, 2):
        transitions.append(Transition(src, tgt, True))
    for tag in tags:
        transitions.append(Transition(tag, tag, True))
        transitions.append(Transition(start, tag, True))
        transitions.append(Transition(tag, start, False))
        transitions.append(Transition(tag, end, True))
        transitions.append(Transition(end, tag, False))
    return transitions


def iob_transitions_legality(
    tags: Set[str], start: str = TokenFunction.GO, end: str = TokenFunction.EOS
) -> List[Transition]:
    """Get transition legality when processing `IOB` tags.

    There are a few rules the govern `IOB` tagging. Spans are allowed to begin with an `I-`
    so a lot of the rules other span encoding formats about not transitioning from `O` to
    and `I-` don't apply. The main rules are around the use of the `B-` token. In `IOB` we
    are only allowed to start a token with a `B-` when it is the start of a new span that
    directly follows (touches) a previous span of the same time. This translates into rules
    that `B-` tokens can only follow tags that have the same type (either `B-` or `I-`)

    Args:
        tags: The tags that we can assign to tokens.
        start: A special tag representing the start of all sequences.
        end: A special tag representing the end of all sequences.

    Returns:
        The list of transitions.
    """
    transitions = []
    for src in chain(tags, [start, end]):
        src_func = extract_function(src)
        src_type = extract_type(src)
        for tgt in chain(tags, [start, end]):
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


def bio_transitions_legality(
    tags: Set[str], start: str = TokenFunction.GO, end: str = TokenFunction.EOS
) -> List[Transition]:
    """Get transition legality when processing `BIO` tags.

    **TODO**

    Args:
        tags: The tags that we can assign to tokens.
        start: A special tag representing the start of all sequences.
        end: A special tag representing the end of all sequences.

    Returns:
        The list of transitions.
    """
    transitions = []
    for src in chain(tags, [start, end]):
        src_func = extract_function(src)
        src_type = extract_type(src)
        for tgt in chain(tags, [start, end]):
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


def with_end_transitions_legality(
    tags: Set[str], span_format: SpanFormat, start: str = TokenFunction.GO, end: str = TokenFunction.EOS
) -> List[Transition]:
    """Get transition legality when processing tags when the encoding scheme has a `end` token function.

    **TODO**

    Note:
        Several span formats like `IOBES`, `BILOU`, and `BMEOW` are the same except for the value
        of some of the `TokenFunction` (`IOBES` has `E` for the end while `BILOU` has `L`). Other
        than these differences these all behave the same way. This function parses all of these
        formats by comparing to the things like the `SpanFormat.BEGIN` instead of the literal
        string. This is the underlying implementation but the user facing function to get the
        transitions for a specific encoding scheme should be used.

    Args:
        tags: The tags that we can assign to tokens.
        span_format: The `SpanFormat` we are using for these tags.
        start: A special tag representing the start of all sequences.
        end: A special tag representing the end of all sequences.

    Returns:
        The list of transitions.
    """
    transitions = []
    for src in chain(tags, [start, end]):
        src_func = extract_function(src)
        src_type = extract_type(src)
        for tgt in chain(tags, [start, end]):
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


def iobes_transitions_legality(
    tags: Set[str], start: str = TokenFunction.GO, end: str = TokenFunction.EOS
) -> List[Transition]:
    """Get transition legality when processing `IOBES` tags.

    **TODO**

    Args:
        tags: The tags that we can assign to tokens.
        start: A special tag representing the start of all sequences.
        end: A special tag representing the end of all sequences.

    Returns:
        The list of transitions.
    """
    return with_end_transtitions_legality(tags, IOBES, start, end)


def bilou_transitions_legality(
    tags: Set[str], start: str = TokenFunction.GO, end: str = TokenFunction.EOS
) -> List[Transition]:
    """Get transition legality when processing `BILOU` tags.

    **TODO**

    Args:
        tags: The tags that we can assign to tokens.
        start: A special tag representing the start of all sequences.
        end: A special tag representing the end of all sequences.

    Returns:
        The list of transitions.
    """
    return with_end_transtitions_legality(tags, BILOU, start, end)


def bmeow_transitions_legality(
    tags: Set[str], start: str = TokenFunction.GO, end: str = TokenFunction.EOS
) -> List[Transition]:
    """Get transition legality when processing `BMEOW` tags.

    **TODO**

    Args:
        tags: The tags that we can assign to tokens.
        start: A special tag representing the start of all sequences.
        end: A special tag representing the end of all sequences.

    Returns:
        The list of transitions.
    """
    return with_end_transtitions_legality(tags, BMEOW, start, end)


bmewo_transitions_legality = bmeow_transitions_legality


def transitions_to_tuple_map(transitions: List[Transition]) -> Dict[Tuple[str, str], bool]:
    """Convert the list of transitions to a dictionary keyed by the `(source, target)` tuple.

    This data structure is useful when given a pair of states you want to check if the transition
    is legal in O(1) time.

    Args:
        transitions: The list of transitions.

    Returns:
        A dictionary mapping `(source, target)` pairs to the legality of that transition.
    """
    return {(src, tgt): valid for src, tgt, valid in transitions}


def transitions_to_map(transitions: List[Transition]) -> Dict[str, Dict[str, bool]]:
    """Convert the list of transitions into nested dictionaries keyed by the states.

    The data format is a dictionary mapping `source` to a dictionary of `target`. This inner
    dictionary has the legality of the transition as values. For example `result[src][tgt]`
    being `True` means that the transition from src to tgt is valid while a `False` means
    it is illegal.

    This data structure is useful when given a state you want to see the legality of transitions
    from it to other states.

    Args:
        transitions: The list of transitions.

    Returns:
        Nested dictionaries representing the legality of transitions.
    """
    mapping = {}
    for src, tgt, valid in transitions:
        to = mapping.setdefault(src, {})
        to[tgt] = valid
    return mapping


def transitions_to_mask(transitions: List[Transition], vocabulary: Dict[str, int]) -> "np.ndarray":
    """Convert the list of transitions into a mask.

    The starting state is represented by the row index in the mask while the ending state is represented
    by the column index. A value of one in the mask means the transition was legal while a zero means
    it was illegal. For example, `mask[src, tgt] == 1` is means the transition from src to tgt was allowed
    while a zero means it is not.

    This data structure is useful when you have a transition matrix that represents something like the
    probability of transitions between states and you want to zero out the value for illegal transitions.

    Note:
        This function has a dependency on `numpy`. This is an optional dependency for the `iobes`
        library and can installed with `pip install iobes[mask]`.

    Args:
        transitions: The list of transitions.
        vocabulary: A mapping of state name to index. This is used to figure out where to place
            the state value in the mask.

    Returns:
        A mask representing the legal and illegal transitions.
    """
    try:
        import numpy as np
    except ImportError as e:
        LOGGER.critical(
            "Could not import the `numpy` library which is needed to create a transition mask. Use `pip install iobes[mask] to include the optional `numpy` dependency."
        )
        raise e
    mask = np.zeros((len(vocabulary), len(vocabulary)))
    for src, tgt, value in transitions:
        if value:
            mask[vocabulary[src], vocabulary[tgt]] = 1
    return mask
